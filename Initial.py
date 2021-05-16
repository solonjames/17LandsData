import csv
import numpy as np

initalArray = np.zeros(699)


def generateCardDictionary(header, startingCardIndex):
    cardDict = {}
    reverse = {}
    counter = 0
    for name in header[startingCardIndex:]:
        cardName = name.replace("pack_card_", "")
        cardDict[cardName] = counter
        reverse[counter] = cardName
        counter = counter + 1
    return cardDict, reverse


def getPickLists(path, numDrafts):
    with open(path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)

        cardDict, num2card = generateCardDictionary(header, 13)

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
    wins, losses = listToPairwise(686, totalList, winList, lossList)

    pairwiseWinrate = np.nan_to_num(np.divide(wins, wins + losses))

    return pairwiseWinrate, num2card


# pairwiseWinrate, num2card = generatePairwiseWinrate(
#    "draft_data_public.STX.PremierDraft.csv", 75000
# )

winrates = np.load("pairwiseWinrate.npy")

test = np.unravel_index(winrates.argmax(), winrates.shape)

print(test)