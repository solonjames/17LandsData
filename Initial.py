import csv
import numpy as np
import pickle


def generateCardDictionary(header, startingCardIndex, totalCards):
    cardDict = {}
    reverse = {}
    counter = 0
    for name in header[startingCardIndex : startingCardIndex + totalCards]:
        cardName = name.replace("pack_card_", "")
        cardDict[cardName] = counter
        reverse[counter] = cardName
        counter = counter + 1
    return cardDict, reverse


def getPickLists(path, numDrafts):
    with open(path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)

        cardDict, num2card = generateCardDictionary(header, 13, 343)

        totalList = []
        winList = []
        lossList = []
        currentRow = next(reader)
        draftID = currentRow[2]
        for i in range(numDrafts):
            currDraftID = draftID
            pickListNum = []
            while draftID == currDraftID:
                pick1 = cardDict[currentRow[10]]
                pickListNum.append(pick1)
                currentRow = next(reader)
                draftID = currentRow[2]
            totalList.append(pickListNum)
            winList.append(int(currentRow[6]))
            lossList.append(int(currentRow[7]))

    return (totalList, winList, lossList, num2card)


def listToPairwise(maxCardIndex, masterList, winList, lossList):
    wins = np.zeros([maxCardIndex, maxCardIndex])
    losses = np.zeros([maxCardIndex, maxCardIndex])
    for pickList, win, loss in zip(masterList, winList, lossList):
        tempList = []
        for pick in pickList:
            for previous in tempList:
                wins[previous][pick] += win
                losses[previous][pick] += loss
            tempList.append(pick)

    return wins, losses


def generatePairwiseWinrate(path, numDrafts):

    (totalList, winList, lossList, num2card) = getPickLists(path, numDrafts)
    wins, losses = listToPairwise(343, totalList, winList, lossList)

    pairwiseWinrate = np.nan_to_num(np.divide(wins, wins + losses))

    return pairwiseWinrate, num2card


def getPick(pairwiseWinrate, pickedCards, cardsInPack):
    maxSum = 0
    pick = -1
    for potentialPick in cardsInPack:
        tempSum = 0
        for pickedCard in pickedCards:
            tempSum += pairwiseWinrate[pickedCard][potentialPick]
        if tempSum > maxSum:
            maxSum = tempSum
            pick = potentialPick

    return pick, maxSum / len(pickedCards)


pairwiseWinrate, num2card = generatePairwiseWinrate(
    "draft_data_public.STX.PremierDraft.csv", 75000
)

with open("pairwiseWinrate.npy", "wb") as f:
    np.save(f, pairwiseWinrate)

with open("num2card.pickle", "wb") as handle:
    pickle.dump(num2card, handle, protocol=pickle.HIGHEST_PROTOCOL)

winrates = np.load("pairwiseWinrate.npy")
with open("num2card.pickle", "rb") as handle:
    num2card = pickle.load(handle)

test, rate = getPick(
    winrates,
    [245, 261, 231, 277, 291, 133, 198, 188, 337],
    [176, 244, 104, 53, 284, 217],
)

print(test)
print(num2card[test])
print(rate)