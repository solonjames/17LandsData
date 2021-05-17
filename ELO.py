import csv
import numpy as np
import pickle


def generateCardDictionary(header, startingCardIndex, totalCards):
    card2num = {}
    num2card = {}
    counter = 0
    for name in header[startingCardIndex : startingCardIndex + totalCards]:
        cardName = name.replace("pack_card_", "")
        card2num[cardName] = counter
        num2card[counter] = cardName
        counter = counter + 1
    return card2num, num2card


def getEloDelta(R1, R2, K):
    Q1 = 10 ** (R1 / 400)
    Q2 = 10 ** (R2 / 400)
    E1 = Q1 / (Q1 + Q2)
    E2 = 1 - E1
    delta1 = K * (1 - E1)
    delta2 = K * (-E2)
    return delta1, delta2


def generateEloMatrix(path, numDrafts, totalCards):
    eloMatrix = np.ones([totalCards, totalCards]) * 1200
    gemPayouts = [50, 100, 250, 1000, 1400, 1600, 1800, 2200]
    with open(path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)

        card2num, num2card = generateCardDictionary(header, 13, 343)

        currentRow = next(reader)
        draftID = currentRow[2]
        for i in range(numDrafts):
            draftWins = int(currentRow[6])
            if draftWins < 0 or draftWins > 7:
                K = 10
            else:
                K = gemPayouts[draftWins] / 100
            currDraftID = draftID
            previousPickList = []
            while draftID == currDraftID:
                currentPick = card2num[currentRow[10]]
                inPackArray = np.array(currentRow[13:356]) == "1"
                cardsInPack = np.arange(totalCards)[inPackArray]

                for rejectedPick in cardsInPack:
                    if rejectedPick != currentPick:
                        for previous in previousPickList:
                            R1 = eloMatrix[previous][currentPick]
                            R2 = eloMatrix[previous][rejectedPick]
                            delta1, delta2 = getEloDelta(R1, R2, K)
                            eloMatrix[previous][currentPick] += delta1
                            eloMatrix[previous][rejectedPick] += delta2
                previousPickList.append(currentPick)
                currentRow = next(reader)
                draftID = currentRow[2]
            if (i % (numDrafts / 10)) == 0:
                print(i)
                test = np.unravel_index(eloMatrix.argmax(), eloMatrix.shape)
                print(num2card[test[0]])
                print(num2card[test[1]])
                print(eloMatrix[test[0]][test[1]])

    return eloMatrix


# eloMatrix = generateEloMatrix("draft_data_public.STX.PremierDraft.csv", 75000, 343)

# with open("eloMatrix.npy", "wb") as f:
#     np.save(f, eloMatrix)
