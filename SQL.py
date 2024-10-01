#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Returns a dict of SQL statements used in fpdb.
"""
from __future__ import print_function
#    Copyright 2008-2011, Ray E. Barker
#   
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#   
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#   
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

#    NOTES:  The sql statements use the placeholder %s for bind variables
#            which is then replaced by ? for sqlite. Comments can be included 
#            within sql statements using C style /* ... */ comments, BUT
#            THE COMMENTS MUST NOT INCLUDE %s OR ?.

########################################################################

#    Standard Library modules

import re

#    pyGTK modules

#    FreePokerTools modules

class Sql(object):
   
    def __init__(self, game='holdem', db_server='sqlite'):
        self.query = {}
###############################################################################3
#    Support for the Free Poker DataBase = fpdb   http://fpdb.sourceforge.net/
#

        ################################
        # List tables
        ################################
        self.query['list_tables'] = """SELECT name FROM sqlite_master
        WHERE type='table'
        ORDER BY name;"""

        ################################
        # List indexes
        ################################
        self.query['list_indexes'] = """SELECT name FROM sqlite_master
                                        WHERE type='index'
                                        ORDER BY name;"""

        ##################################################################
        # Drop Tables
        ##################################################################

        self.query['drop_table'] = """DROP TABLE IF EXISTS """   


        ##################################################################
        # Set transaction isolation level
        ##################################################################

        self.query['set tx level'] = """ """


        ################################
        # Select basic info
        ################################

        self.query['getSiteId'] = """SELECT id from Sites where name = %s"""

        self.query['getGames'] = """SELECT DISTINCT category from Gametypes"""
        
        self.query['getCurrencies'] = """SELECT DISTINCT currency from Gametypes ORDER BY currency"""
        
        self.query['getLimits'] = """SELECT DISTINCT bigBlind from Gametypes ORDER by bigBlind DESC"""

        self.query['getTourneyTypesIds'] = "SELECT id FROM TourneyTypes"
        
        self.query['getTourneyTypes'] = "SELECT DISTINCT tourneyName FROM Tourneys"

        self.query['getTourneyNames'] = "SELECT tourneyName FROM Tourneys"

        ################################
        # Create Settings
        ################################
        self.query['createSettingsTable'] = """CREATE TABLE Settings
        (version INTEGER NOT NULL) """
            
        ################################
        # Create RawHands (this table is all but identical with RawTourneys)
        ################################
        self.query['createRawHands'] = """CREATE TABLE RawHands (
                    id INTEGER PRIMARY KEY,
                    handId BIGINT NOT NULL,
                    rawHand TEXT NOT NULL,
                    complain BOOLEAN NOT NULL DEFAULT FALSE)"""
        
        ################################
        # Create RawTourneys (this table is all but identical with RawHands)
        ################################
        self.query['createRawTourneys'] = """CREATE TABLE RawTourneys (
                    id INTEGER PRIMARY KEY,
                    tourneyId BIGINT NOT NULL,
                    rawTourney TEXT NOT NULL,
                    complain BOOLEAN NOT NULL DEFAULT FALSE)"""
                        
        ################################
        # Create Actions
        ################################

        self.query['createActionsTable'] = """CREATE TABLE Actions (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    code TEXT NOT NULL)"""
                        
        ################################
        # Create Rank
        ################################

        self.query['createRankTable'] = """CREATE TABLE Rank (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL)"""
                        
        ################################
        # Create StartCards
        ################################

        self.query['createStartCardsTable'] = """CREATE TABLE StartCards (
                    id INTEGER PRIMARY KEY,
                    category TEXT NOT NULL,
                    name TEXT NOT NULL,
                    rank SMALLINT NOT NULL,
                    combinations SMALLINT NOT NULL)"""
                        
        ################################
        # Create Sites
        ################################

        self.query['createSitesTable'] = """CREATE TABLE Sites (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    code TEXT NOT NULL)"""

        ################################
        # Create Backings
        ################################
        
        self.query['createBackingsTable'] = """CREATE TABLE Backings (
                    id INTEGER PRIMARY KEY,
                    tourneysPlayersId INT NOT NULL,
                    playerId INT NOT NULL,
                    buyInPercentage REAL UNSIGNED NOT NULL,
                    payOffPercentage REAL UNSIGNED NOT NULL)"""
        
        ################################
        # Create Gametypes
        ################################

        self.query['createGametypesTable'] = """CREATE TABLE Gametypes (
                    id INTEGER PRIMARY KEY NOT NULL,
                    siteId INTEGER NOT NULL,
                    currency TEXT NOT NULL,
                    type TEXT NOT NULL,
                    base TEXT NOT NULL,
                    category TEXT NOT NULL,
                    limitType TEXT NOT NULL,
                    hiLo TEXT NOT NULL,
                    mix TEXT NOT NULL,
                    smallBlind INTEGER,
                    bigBlind INTEGER,
                    smallBet INTEGER NOT NULL,
                    bigBet INTEGER NOT NULL,
                    maxSeats INT NOT NULL,
                    ante INT NOT NULL,
                    buyinType TEXT NOT NULL,
                    fast INT,
                    newToGame INT,
                    homeGame INT,
                    split INT,
                    FOREIGN KEY(siteId) REFERENCES Sites(id) ON DELETE CASCADE)"""


        ################################
        # Create Players
        ################################

        self.query['createPlayersTable'] = """CREATE TABLE Players (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    siteId INTEGER,
                    hero BOOLEAN,
                    chars TEXT,
                    comment TEXT,
                    commentTs timestamp,
                    profil TEXT,
                    color_code TEXT DEFAULT '#FFFFFF',
                    symbol TEXT DEFAULT '★',  
                    FOREIGN KEY(siteId) REFERENCES Sites(id) ON DELETE CASCADE)"""


        ################################
        # Create Autorates
        ################################

        self.query['createAutoratesTable'] = """CREATE TABLE Autorates (
                        id INTEGER PRIMARY KEY,
                        playerId INT,
                        gametypeId INT,
                        description TEXT,
                        shortDesc TEXT,
                        ratingTime timestamp,
                        handCount int)"""


        ################################
        # Create Hands
        ################################

        self.query['createHandsTable'] = """CREATE TABLE Hands (
                        id INTEGER PRIMARY KEY,
                        tableName TEXT(50) NOT NULL,
                        siteHandNo INT NOT NULL,
                        tourneyId INT,
                        gametypeId INT NOT NULL,
                        sessionId INT,
                        fileId INT NOT NULL,
                        startTime timestamp NOT NULL,
                        importTime timestamp NOT NULL,
                        seats INT NOT NULL,
                        heroSeat INT NOT NULL,
                        maxPosition INT NOT NULL,
                        boardcard1 INT,  /* 0=none, 1-13=2-Ah 14-26=2-Ad 27-39=2-Ac 40-52=2-As */
                        boardcard2 INT,
                        boardcard3 INT,
                        boardcard4 INT,
                        boardcard5 INT,
                        texture INT,
                        runItTwice BOOLEAN,
                        playersVpi INT NOT NULL,         /* num of players vpi */
                        playersAtStreet1 INT NOT NULL,   /* num of players seeing flop/street4 */
                        playersAtStreet2 INT NOT NULL,
                        playersAtStreet3 INT NOT NULL,
                        playersAtStreet4 INT NOT NULL,
                        playersAtShowdown INT NOT NULL,
                        street0Raises INT NOT NULL, /* num small bets paid to see flop/street4, including blind */
                        street1Raises INT NOT NULL, /* num small bets paid to see turn/street5 */
                        street2Raises INT NOT NULL, /* num big bets paid to see river/street6 */
                        street3Raises INT NOT NULL, /* num big bets paid to see sd/street7 */
                        street4Raises INT NOT NULL, /* num big bets paid to see showdown */
                        street0Pot INT,                 /* pot size at preflop/street3 */
                        street1Pot INT,                 /* pot size at flop/street4 */
                        street2Pot INT,                 /* pot size at turn/street5 */
                        street3Pot INT,                 /* pot size at river/street6 */
                        street4Pot INT,                 /* pot size at sd/street7 */
                        finalPot INT,                   /* final pot size */
                        comment TEXT,
                        commentTs timestamp)"""
                            
        ################################
        # Create Boards
        ################################

        self.query['createBoardsTable'] = """CREATE TABLE Boards (
                        id INTEGER PRIMARY KEY,
                        handId INT NOT NULL,
                        boardId INT,
                        boardcard1 INT,  /* 0=none, 1-13=2-Ah 14-26=2-Ad 27-39=2-Ac 40-52=2-As */
                        boardcard2 INT,
                        boardcard3 INT,
                        boardcard4 INT,
                        boardcard5 INT)"""


     ################################
        # Create TourneyTypes
        ################################

        self.query['createTourneyTypesTable'] = """CREATE TABLE TourneyTypes (
                    id INTEGER PRIMARY KEY,
                    siteId INT NOT NULL,
                    currency VARCHAR(4),
                    buyin INT,
                    fee INT,
                    category TEXT,
                    limitType TEXT,
                    buyInChips INT,
                    stack VARCHAR(8),
                    maxSeats INT,
                    rebuy BOOLEAN,
                    rebuyCost INT,
                    rebuyFee INT,
                    rebuyChips INT,
                    addOn BOOLEAN,
                    addOnCost INT,
                    addOnFee INT,
                    addOnChips INT,
                    knockout BOOLEAN,
                    koBounty INT,
                    progressive BOOLEAN,
                    step BOOLEAN,
                    stepNo INT,
                    chance BOOLEAN,
                    chanceCount INT,
                    speed TEXT,
                    shootout BOOLEAN,
                    matrix BOOLEAN,
                    multiEntry BOOLEAN,
                    reEntry BOOLEAN,
                    fast BOOLEAN,
                    newToGame BOOLEAN,
                    homeGame BOOLEAN,
                    split BOOLEAN,
                    sng BOOLEAN,
                    fifty50 BOOLEAN,
                    time BOOLEAN,
                    timeAmt INT,
                    satellite BOOLEAN,
                    doubleOrNothing BOOLEAN,
                    cashOut BOOLEAN,
                    onDemand BOOLEAN,
                    flighted BOOLEAN,
                    guarantee BOOLEAN,
                    guaranteeAmt INT)"""

        ################################
        # Create Tourneys
        ################################

        self.query['createTourneysTable'] = """CREATE TABLE Tourneys (
                    id INTEGER PRIMARY KEY,
                    tourneyTypeId INT,
                    sessionId INT,
                    siteTourneyNo INT,
                    entries INT,
                    prizepool INT,
                    startTime timestamp,
                    endTime timestamp,
                    tourneyName TEXT,
                    totalRebuyCount INT,
                    totalAddOnCount INT,
                    added INT,
                    addedCurrency VARCHAR(4),
                    comment TEXT,
                    commentTs timestamp)"""
                        
        ################################
        # Create HandsPlayers
        ################################

        self.query['createHandsPlayersTable'] = """CREATE TABLE HandsPlayers (
                    id INTEGER PRIMARY KEY,
                    handId INT NOT NULL,
                    playerId INT NOT NULL,
                    startCash INT NOT NULL,
                    effStack INT NOT NULL,
                    startBounty INT,
                    endBounty INT,
                    position TEXT,
                    seatNo INT NOT NULL,
                    sitout BOOLEAN NOT NULL,
                    
                    card1 INT NOT NULL,  /* 0=none, 1-13=2-Ah 14-26=2-Ad 27-39=2-Ac 40-52=2-As */
                    card2 INT NOT NULL,
                    card3 INT,
                    card4 INT,
                    card5 INT,
                    card6 INT,
                    card7 INT,
                    card8 INT,  /* cards 8-20 for draw hands */
                    card9 INT,
                    card10 INT,
                    card11 INT,
                    card12 INT,
                    card13 INT,
                    card14 INT,
                    card15 INT,
                    card16 INT,
                    card17 INT,
                    card18 INT,
                    card19 INT,
                    card20 INT,
                    startCards INT,
                    
                    common INT NOT NULL,
                    committed INT NOT NULL,
                    winnings INT NOT NULL,
                    rake INT NOT NULL,
                    rakeDealt decimal NOT NULL,
                    rakeContributed decimal NOT NULL,
                    rakeWeighted decimal NOT NULL,
                    totalProfit INT,
                    allInEV decimal,
                    comment TEXT,
                    commentTs timestamp,
                    tourneysPlayersId INT,

                    wonWhenSeenStreet1 INT,
                    wonWhenSeenStreet2 INT,
                    wonWhenSeenStreet3 INT,
                    wonWhenSeenStreet4 INT,
                    wonAtSD INT,
                        
                    street0VPIChance INT,
                    street0VPI INT,
                    street0AggrChance INT,
                    street0Aggr INT,
                    street0CalledRaiseChance INT,
                    street0CalledRaiseDone INT,
                    street0_2BChance INT,
                    street0_2BDone INT,
                    street0_3BChance INT,
                    street0_3BDone INT,
                    street0_4BChance INT,
                    street0_4BDone INT,
                    street0_C4BChance INT,
                    street0_C4BDone INT,
                    street0_FoldTo2BChance INT,
                    street0_FoldTo2BDone INT,
                    street0_FoldTo3BChance INT,
                    street0_FoldTo3BDone INT,
                    street0_FoldTo4BChance INT,
                    street0_FoldTo4BDone INT,
                    street0_SqueezeChance INT,
                    street0_SqueezeDone INT,

                    raiseToStealChance INT,
                    raiseToStealDone INT,
                    stealChance INT,
                    stealDone INT,
                    success_Steal INT,

                    street1Seen INT,
                    street2Seen INT,
                    street3Seen INT,
                    street4Seen INT,
                    sawShowdown INT,
                    showed      INT,
                        
                    street0AllIn INT,
                    street1AllIn INT,
                    street2AllIn INT,
                    street3AllIn INT,
                    street4AllIn INT,
                    wentAllIn INT,
                        
                    street0InPosition INT,
                    street1InPosition INT,
                    street2InPosition INT,
                    street3InPosition INT,
                    street4InPosition INT,
                    street0FirstToAct INT,
                    street1FirstToAct INT,
                    street2FirstToAct INT,
                    street3FirstToAct INT,
                    street4FirstToAct INT,

                    street1Aggr INT,
                    street2Aggr INT,
                    street3Aggr INT,
                    street4Aggr INT,

                    otherRaisedStreet0 INT,
                    otherRaisedStreet1 INT,
                    otherRaisedStreet2 INT,
                    otherRaisedStreet3 INT,
                    otherRaisedStreet4 INT,
                    foldToOtherRaisedStreet0 INT,
                    foldToOtherRaisedStreet1 INT,
                    foldToOtherRaisedStreet2 INT,
                    foldToOtherRaisedStreet3 INT,
                    foldToOtherRaisedStreet4 INT,

                    raiseFirstInChance INT,
                    raisedFirstIn INT,
                    foldBbToStealChance INT,
                    foldedBbToSteal INT,
                    foldSbToStealChance INT,
                    foldedSbToSteal INT,

                    street1CBChance INT,
                    street1CBDone INT,
                    street2CBChance INT,
                    street2CBDone INT,
                    street3CBChance INT,
                    street3CBDone INT,
                    street4CBChance INT,
                    street4CBDone INT,

                    foldToStreet1CBChance INT,
                    foldToStreet1CBDone INT,
                    foldToStreet2CBChance INT,
                    foldToStreet2CBDone INT,
                    foldToStreet3CBChance INT,
                    foldToStreet3CBDone INT,
                    foldToStreet4CBChance INT,
                    foldToStreet4CBDone INT,

                    street1CheckCallRaiseChance INT,
                    street1CheckCallDone INT,
                    street1CheckRaiseDone INT,
                    street2CheckCallRaiseChance INT,
                    street2CheckCallDone INT,
                    street2CheckRaiseDone INT,
                    street3CheckCallRaiseChance INT,
                    street3CheckCallDone INT,
                    street3CheckRaiseDone INT,
                    street4CheckCallRaiseChance INT,
                    street4CheckCallDone INT,
                    street4CheckRaiseDone INT,

                    street0Calls INT,
                    street1Calls INT,
                    street2Calls INT,
                    street3Calls INT,
                    street4Calls INT,
                    street0Bets INT,
                    street1Bets INT,
                    street2Bets INT,
                    street3Bets INT,
                    street4Bets INT,
                    street0Raises INT,
                    street1Raises INT,
                    street2Raises INT,
                    street3Raises INT,
                    street4Raises INT,
                    street1Discards INT,
                    street2Discards INT,
                    street3Discards INT,
                        
                    handString TEXT,
                    actionString VARCHAR(15))
                    """


     ################################
        # Create TourneysPlayers
        ################################

        self.query['createTourneysPlayersTable'] = """CREATE TABLE TourneysPlayers (
                    id INTEGER PRIMARY KEY,
                    tourneyId INT,
                    playerId INT,
                    entryId INT,
                    rank INT,
                    winnings INT,
                    winningsCurrency VARCHAR(4),
                    rebuyCount INT,
                    addOnCount INT,
                    koCount decimal,
                    comment TEXT,
                    commentTs timestamp,
                    FOREIGN KEY (tourneyId) REFERENCES Tourneys(id),
                    FOREIGN KEY (playerId) REFERENCES Players(id)
                    )"""


        ################################
        # Create HandsActions
        ################################

        self.query['createHandsActionsTable'] = """CREATE TABLE HandsActions (
                    id INTEGER PRIMARY KEY,
                    handId INT NOT NULL,
                    playerId INT NOT NULL,
                    street SMALLINT,
                    actionNo SMALLINT,
                    streetActionNo SMALLINT,
                    actionId SMALLINT,
                    amount INT,
                    raiseTo INT,
                    amountCalled INT,
                    numDiscarded SMALLINT,
                    cardsDiscarded TEXT,
                    allIn BOOLEAN
                    )"""


        ################################
        # Create HandsStove
        ################################

        self.query['createHandsStoveTable'] = """CREATE TABLE HandsStove (
                    id INTEGER PRIMARY KEY,
                    handId INT NOT NULL,
                    playerId INT NOT NULL,
                    streetId INT,
                    boardId INT,
                    hiLo TEXT NOT NULL,
                    rankId INT,
                    value INT,
                    cards TEXT,
                    ev decimal
                    )"""
                        
        ################################
        # Create HandsPots
        ################################

        self.query['createHandsPotsTable'] = """CREATE TABLE HandsPots (
                    id INTEGER PRIMARY KEY,
                    handId INT NOT NULL,
                    potId INT,
                    boardId INT,
                    hiLo TEXT NOT NULL,
                    playerId INT NOT NULL,
                    pot INT,
                    collected INT,
                    rake INT
                    )"""
                        
        ################################
        # Create Files
        ################################
        
        self.query['createFilesTable'] = """CREATE TABLE Files (
                    id INTEGER PRIMARY KEY,
                    file TEXT NOT NULL,
                    site VARCHAR(32),
                    type VARCHAR(7),
                    startTime timestamp NOT NULL,
                    lastUpdate timestamp NOT NULL,
                    endTime timestamp,
                    hands INT,
                    storedHands INT,
                    dups INT,
                    partial INT,
                    skipped INT,
                    errs INT,
                    ttime100 INT,
                    finished BOOLEAN
                    )"""

        ################################
        # Create HudCache
        ################################

        self.query['createHudCacheTable'] = """CREATE TABLE HudCache (
                    id INTEGER PRIMARY KEY,
                    gametypeId INT,
                    playerId INT,
                    seats INT,
                    position TEXT,
                    tourneyTypeId INT,
                    styleKey TEXT NOT NULL,  /* 1st char is style (A/T/H/S), other 6 are the key */
                    n INT,                        
                    street0VPIChance INT,
                    street0VPI INT,
                    street0AggrChance INT,
                    street0Aggr INT,
                    street0CalledRaiseChance INT,
                    street0CalledRaiseDone INT,
                    street0_2BChance INT,
                    street0_2BDone INT,
                    street0_3BChance INT,
                    street0_3BDone INT,
                    street0_4BChance INT,
                    street0_4BDone INT,
                    street0_C4BChance INT,
                    street0_C4BDone INT,
                    street0_FoldTo2BChance INT,
                    street0_FoldTo2BDone INT,
                    street0_FoldTo3BChance INT,
                    street0_FoldTo3BDone INT,
                    street0_FoldTo4BChance INT,
                    street0_FoldTo4BDone INT,
                    street0_SqueezeChance INT,
                    street0_SqueezeDone INT,
                    raiseToStealChance INT,
                    raiseToStealDone INT,
                    stealChance INT,
                    stealDone INT,
                    success_Steal INT,
                    street1Seen INT,
                    street2Seen INT,
                    street3Seen INT,
                    street4Seen INT,
                    sawShowdown INT,
                    street1Aggr INT,
                    street2Aggr INT,
                    street3Aggr INT,
                    street4Aggr INT,
                    otherRaisedStreet0 INT,
                    otherRaisedStreet1 INT,
                    otherRaisedStreet2 INT,
                    otherRaisedStreet3 INT,
                    otherRaisedStreet4 INT,
                    foldToOtherRaisedStreet0 INT,
                    foldToOtherRaisedStreet1 INT,
                    foldToOtherRaisedStreet2 INT,
                    foldToOtherRaisedStreet3 INT,
                    foldToOtherRaisedStreet4 INT,
                    wonWhenSeenStreet1 INT,
                    wonWhenSeenStreet2 INT,
                    wonWhenSeenStreet3 INT,
                    wonWhenSeenStreet4 INT,
                    wonAtSD INT,
                    raiseFirstInChance INT,
                    raisedFirstIn INT,
                    foldBbToStealChance INT,
                    foldedBbToSteal INT,
                    foldSbToStealChance INT,
                    foldedSbToSteal INT,
                    street1CBChance INT,
                    street1CBDone INT,
                    street2CBChance INT,
                    street2CBDone INT,
                    street3CBChance INT,
                    street3CBDone INT,
                    street4CBChance INT,
                    street4CBDone INT,
                    foldToStreet1CBChance INT,
                    foldToStreet1CBDone INT,
                    foldToStreet2CBChance INT,
                    foldToStreet2CBDone INT,
                    foldToStreet3CBChance INT,
                    foldToStreet3CBDone INT,
                    foldToStreet4CBChance INT,
                    foldToStreet4CBDone INT,
                    common INT,
                    committed INT,
                    winnings INT,
                    rake INT,
                    rakeDealt decimal,
                    rakeContributed decimal,
                    rakeWeighted decimal,
                    totalProfit INT,
                    allInEV decimal,
                    showdownWinnings INT,
                    nonShowdownWinnings INT,
                    street1CheckCallRaiseChance INT,
                    street1CheckCallDone INT,
                    street1CheckRaiseDone INT,
                    street2CheckCallRaiseChance INT,
                    street2CheckCallDone INT,
                    street2CheckRaiseDone INT,
                    street3CheckCallRaiseChance INT,
                    street3CheckCallDone INT,
                    street3CheckRaiseDone INT,
                    street4CheckCallRaiseChance INT,
                    street4CheckCallDone INT,
                    street4CheckRaiseDone INT,
                    street0Calls INT,
                    street1Calls INT,
                    street2Calls INT,
                    street3Calls INT,
                    street4Calls INT,
                    street0Bets INT,
                    street1Bets INT,
                    street2Bets INT,
                    street3Bets INT,
                    street4Bets INT,
                    street0Raises INT,
                    street1Raises INT,
                    street2Raises INT,
                    street3Raises INT,
                    street4Raises INT,
                    street1Discards INT,
                    street2Discards INT,
                    street3Discards INT)
                    """
                        
        ################################
        # Create CardsCache
        ################################

        self.query['createCardsCacheTable'] = """CREATE TABLE CardsCache (
                    id INTEGER PRIMARY KEY,
                    weekId INT,
                    monthId INT,
                    gametypeId INT,
                    tourneyTypeId INT,
                    playerId INT,
                    startCards INT,
                    n INT,                        
                    street0VPIChance INT,
                    street0VPI INT,
                    street0AggrChance INT,
                    street0Aggr INT,
                    street0CalledRaiseChance INT,
                    street0CalledRaiseDone INT,
                    street0_2BChance INT,
                    street0_2BDone INT,
                    street0_3BChance INT,
                    street0_3BDone INT,
                    street0_4BChance INT,
                    street0_4BDone INT,
                    street0_C4BChance INT,
                    street0_C4BDone INT,
                    street0_FoldTo2BChance INT,
                    street0_FoldTo2BDone INT,
                    street0_FoldTo3BChance INT,
                    street0_FoldTo3BDone INT,
                    street0_FoldTo4BChance INT,
                    street0_FoldTo4BDone INT,
                    street0_SqueezeChance INT,
                    street0_SqueezeDone INT,
                    raiseToStealChance INT,
                    raiseToStealDone INT,
                    stealChance INT,
                    stealDone INT,
                    success_Steal INT,
                    street1Seen INT,
                    street2Seen INT,
                    street3Seen INT,
                    street4Seen INT,
                    sawShowdown INT,
                    street1Aggr INT,
                    street2Aggr INT,
                    street3Aggr INT,
                    street4Aggr INT,
                    otherRaisedStreet0 INT,
                    otherRaisedStreet1 INT,
                    otherRaisedStreet2 INT,
                    otherRaisedStreet3 INT,
                    otherRaisedStreet4 INT,
                    foldToOtherRaisedStreet0 INT,
                    foldToOtherRaisedStreet1 INT,
                    foldToOtherRaisedStreet2 INT,
                    foldToOtherRaisedStreet3 INT,
                    foldToOtherRaisedStreet4 INT,
                    wonWhenSeenStreet1 INT,
                    wonWhenSeenStreet2 INT,
                    wonWhenSeenStreet3 INT,
                    wonWhenSeenStreet4 INT,
                    wonAtSD INT,
                    raiseFirstInChance INT,
                    raisedFirstIn INT,
                    foldBbToStealChance INT,
                    foldedBbToSteal INT,
                    foldSbToStealChance INT,
                    foldedSbToSteal INT,
                    street1CBChance INT,
                    street1CBDone INT,
                    street2CBChance INT,
                    street2CBDone INT,
                    street3CBChance INT,
                    street3CBDone INT,
                    street4CBChance INT,
                    street4CBDone INT,
                    foldToStreet1CBChance INT,
                    foldToStreet1CBDone INT,
                    foldToStreet2CBChance INT,
                    foldToStreet2CBDone INT,
                    foldToStreet3CBChance INT,
                    foldToStreet3CBDone INT,
                    foldToStreet4CBChance INT,
                    foldToStreet4CBDone INT,
                    common INT,
                    committed INT,
                    winnings INT,
                    rake INT,
                    rakeDealt decimal,
                    rakeContributed decimal,
                    rakeWeighted decimal,
                    totalProfit INT,
                    allInEV decimal,
                    showdownWinnings INT,
                    nonShowdownWinnings INT,
                    street1CheckCallRaiseChance INT,
                    street1CheckCallDone INT,
                    street1CheckRaiseDone INT,
                    street2CheckCallRaiseChance INT,
                    street2CheckCallDone INT,
                    street2CheckRaiseDone INT,
                    street3CheckCallRaiseChance INT,
                    street3CheckCallDone INT,
                    street3CheckRaiseDone INT,
                    street4CheckCallRaiseChance INT,
                    street4CheckCallDone INT,
                    street4CheckRaiseDone INT,
                    street0Calls INT,
                    street1Calls INT,
                    street2Calls INT,
                    street3Calls INT,
                    street4Calls INT,
                    street0Bets INT,
                    street1Bets INT,
                    street2Bets INT,
                    street3Bets INT,
                    street4Bets INT,
                    street0Raises INT,
                    street1Raises INT,
                    street2Raises INT,
                    street3Raises INT,
                    street4Raises INT,
                    street1Discards INT,
                    street2Discards INT,
                    street3Discards INT)
                    """
                        
        ################################
        # Create PositionsCache
        ################################

        self.query['createPositionsCacheTable'] = """CREATE TABLE PositionsCache (
                    id INTEGER PRIMARY KEY,
                    weekId INT,
                    monthId INT,
                    gametypeId INT,
                    tourneyTypeId INT,
                    playerId INT,
                    seats INT,
                    maxPosition INT NOT NULL,
                    position TEXT,
                    n INT,
                    street0VPIChance INT,
                    street0VPI INT,
                    street0AggrChance INT,
                    street0Aggr INT,
                    street0CalledRaiseChance INT,
                    street0CalledRaiseDone INT,
                    street0_2BChance INT,
                    street0_2BDone INT,
                    street0_3BChance INT,
                    street0_3BDone INT,
                    street0_4BChance INT,
                    street0_4BDone INT,
                    street0_C4BChance INT,
                    street0_C4BDone INT,
                    street0_FoldTo2BChance INT,
                    street0_FoldTo2BDone INT,
                    street0_FoldTo3BChance INT,
                    street0_FoldTo3BDone INT,
                    street0_FoldTo4BChance INT,
                    street0_FoldTo4BDone INT,
                    street0_SqueezeChance INT,
                    street0_SqueezeDone INT,
                    raiseToStealChance INT,
                    raiseToStealDone INT,
                    stealChance INT,
                    stealDone INT,
                    success_Steal INT,
                    street1Seen INT,
                    street2Seen INT,
                    street3Seen INT,
                    street4Seen INT,
                    sawShowdown INT,
                    street1Aggr INT,
                    street2Aggr INT,
                    street3Aggr INT,
                    street4Aggr INT,
                    otherRaisedStreet0 INT,
                    otherRaisedStreet1 INT,
                    otherRaisedStreet2 INT,
                    otherRaisedStreet3 INT,
                    otherRaisedStreet4 INT,
                    foldToOtherRaisedStreet0 INT,
                    foldToOtherRaisedStreet1 INT,
                    foldToOtherRaisedStreet2 INT,
                    foldToOtherRaisedStreet3 INT,
                    foldToOtherRaisedStreet4 INT,
                    wonWhenSeenStreet1 INT,
                    wonWhenSeenStreet2 INT,
                    wonWhenSeenStreet3 INT,
                    wonWhenSeenStreet4 INT,
                    wonAtSD INT,
                    raiseFirstInChance INT,
                    raisedFirstIn INT,
                    foldBbToStealChance INT,
                    foldedBbToSteal INT,
                    foldSbToStealChance INT,
                    foldedSbToSteal INT,
                    street1CBChance INT,
                    street1CBDone INT,
                    street2CBChance INT,
                    street2CBDone INT,
                    street3CBChance INT,
                    street3CBDone INT,
                    street4CBChance INT,
                    street4CBDone INT,
                    foldToStreet1CBChance INT,
                    foldToStreet1CBDone INT,
                    foldToStreet2CBChance INT,
                    foldToStreet2CBDone INT,
                    foldToStreet3CBChance INT,
                    foldToStreet3CBDone INT,
                    foldToStreet4CBChance INT,
                    foldToStreet4CBDone INT,
                    common INT,
                    committed INT,
                    winnings INT,
                    rake INT,
                    rakeDealt decimal,
                    rakeContributed decimal,
                    rakeWeighted decimal,
                    totalProfit INT,
                    allInEV decimal,
                    showdownWinnings INT,
                    nonShowdownWinnings INT,
                    street1CheckCallRaiseChance INT,
                    street1CheckCallDone INT,
                    street1CheckRaiseDone INT,
                    street2CheckCallRaiseChance INT,
                    street2CheckCallDone INT,
                    street2CheckRaiseDone INT,
                    street3CheckCallRaiseChance INT,
                    street3CheckCallDone INT,
                    street3CheckRaiseDone INT,
                    street4CheckCallRaiseChance INT,
                    street4CheckCallDone INT,
                    street4CheckRaiseDone INT,
                    street0Calls INT,
                    street1Calls INT,
                    street2Calls INT,
                    street3Calls INT,
                    street4Calls INT,
                    street0Bets INT,
                    street1Bets INT,
                    street2Bets INT,
                    street3Bets INT,
                    street4Bets INT,
                    street0Raises INT,
                    street1Raises INT,
                    street2Raises INT,
                    street3Raises INT,
                    street4Raises INT,
                    street1Discards INT,
                    street2Discards INT,
                    street3Discards INT)
                    """
                        
        ################################
        # Create Weeks
        ################################

        self.query['createWeeksTable'] = """CREATE TABLE Weeks (
                        id INTEGER PRIMARY KEY,
                        weekStart timestamp NOT NULL)
                        """
                        
        ################################
        # Create Months
        ################################

        self.query['createMonthsTable'] = """CREATE TABLE Months (
                        id INTEGER PRIMARY KEY,
                        monthStart timestamp NOT NULL)
                        """
                        
        ################################
        # Create Sessions
        ################################

        self.query['createSessionsTable'] = """CREATE TABLE Sessions (
                        id INTEGER PRIMARY KEY,
                        weekId INT,
                        monthId INT,
                        sessionStart timestamp NOT NULL,
                        sessionEnd timestamp NOT NULL)
                        """
                        
        ################################
        # Create SessionsCache
        ################################

        self.query['createSessionsCacheTable'] = """CREATE TABLE SessionsCache (
                    id INTEGER PRIMARY KEY,
                    sessionId INT,
                    startTime timestamp NOT NULL,
                    endTime timestamp NOT NULL,
                    gametypeId INT,
                    playerId INT,
                    n INT,
                    street0VPIChance INT,
                    street0VPI INT,
                    street0AggrChance INT,
                    street0Aggr INT,
                    street0CalledRaiseChance INT,
                    street0CalledRaiseDone INT,
                    street0_2BChance INT,
                    street0_2BDone INT,
                    street0_3BChance INT,
                    street0_3BDone INT,
                    street0_4BChance INT,
                    street0_4BDone INT,
                    street0_C4BChance INT,
                    street0_C4BDone INT,
                    street0_FoldTo2BChance INT,
                    street0_FoldTo2BDone INT,
                    street0_FoldTo3BChance INT,
                    street0_FoldTo3BDone INT,
                    street0_FoldTo4BChance INT,
                    street0_FoldTo4BDone INT,
                    street0_SqueezeChance INT,
                    street0_SqueezeDone INT,
                    raiseToStealChance INT,
                    raiseToStealDone INT,
                    stealChance INT,
                    stealDone INT,
                    success_Steal INT,
                    street1Seen INT,
                    street2Seen INT,
                    street3Seen INT,
                    street4Seen INT,
                    sawShowdown INT,
                    street1Aggr INT,
                    street2Aggr INT,
                    street3Aggr INT,
                    street4Aggr INT,
                    otherRaisedStreet0 INT,
                    otherRaisedStreet1 INT,
                    otherRaisedStreet2 INT,
                    otherRaisedStreet3 INT,
                    otherRaisedStreet4 INT,
                    foldToOtherRaisedStreet0 INT,
                    foldToOtherRaisedStreet1 INT,
                    foldToOtherRaisedStreet2 INT,
                    foldToOtherRaisedStreet3 INT,
                    foldToOtherRaisedStreet4 INT,                        
                    wonWhenSeenStreet1 INT,
                    wonWhenSeenStreet2 INT,
                    wonWhenSeenStreet3 INT,
                    wonWhenSeenStreet4 INT,
                    wonAtSD INT,
                    raiseFirstInChance INT,
                    raisedFirstIn INT,
                    foldBbToStealChance INT,
                    foldedBbToSteal INT,
                    foldSbToStealChance INT,
                    foldedSbToSteal INT,
                    street1CBChance INT,
                    street1CBDone INT,
                    street2CBChance INT,
                    street2CBDone INT,
                    street3CBChance INT,
                    street3CBDone INT,
                    street4CBChance INT,
                    street4CBDone INT,
                    foldToStreet1CBChance INT,
                    foldToStreet1CBDone INT,
                    foldToStreet2CBChance INT,
                    foldToStreet2CBDone INT,
                    foldToStreet3CBChance INT,
                    foldToStreet3CBDone INT,
                    foldToStreet4CBChance INT,
                    foldToStreet4CBDone INT,
                    common INT,
                    committed INT,
                    winnings INT,
                    rake INT,
                    rakeDealt decimal,
                    rakeContributed decimal,
                    rakeWeighted decimal,
                    totalProfit INT,
                    allInEV decimal,
                    showdownWinnings INT,
                    nonShowdownWinnings INT,
                    street1CheckCallRaiseChance INT,
                    street1CheckCallDone INT,
                    street1CheckRaiseDone INT,
                    street2CheckCallRaiseChance INT,
                    street2CheckCallDone INT,
                    street2CheckRaiseDone INT,
                    street3CheckCallRaiseChance INT,
                    street3CheckCallDone INT,
                    street3CheckRaiseDone INT,
                    street4CheckCallRaiseChance INT,
                    street4CheckCallDone INT,
                    street4CheckRaiseDone INT,
                    street0Calls INT,
                    street1Calls INT,
                    street2Calls INT,
                    street3Calls INT,
                    street4Calls INT,
                    street0Bets INT,
                    street1Bets INT,
                    street2Bets INT,
                    street3Bets INT,
                    street4Bets INT,
                    street0Raises INT,
                    street1Raises INT,
                    street2Raises INT,
                    street3Raises INT,
                    street4Raises INT,
                    street1Discards INT,
                    street2Discards INT,
                    street3Discards INT)
                    """
                        
        ################################
        # Create TourneysCache
        ################################

        self.query['createTourneysCacheTable'] = """CREATE TABLE TourneysCache (
                    id INTEGER PRIMARY KEY,
                    sessionId INT,
                    startTime timestamp NOT NULL,
                    endTime timestamp NOT NULL,
                    tourneyId INT,
                    playerId INT,
                    n INT,
                    street0VPIChance INT,
                    street0VPI INT,
                    street0AggrChance INT,
                    street0Aggr INT,
                    street0CalledRaiseChance INT,
                    street0CalledRaiseDone INT,
                    street0_2BChance INT,
                    street0_2BDone INT,
                    street0_3BChance INT,
                    street0_3BDone INT,
                    street0_4BChance INT,
                    street0_4BDone INT,
                    street0_C4BChance INT,
                    street0_C4BDone INT,
                    street0_FoldTo2BChance INT,
                    street0_FoldTo2BDone INT,
                    street0_FoldTo3BChance INT,
                    street0_FoldTo3BDone INT,
                    street0_FoldTo4BChance INT,
                    street0_FoldTo4BDone INT,
                    street0_SqueezeChance INT,
                    street0_SqueezeDone INT,
                    raiseToStealChance INT,
                    raiseToStealDone INT,
                    stealChance INT,
                    stealDone INT,
                    success_Steal INT,
                    street1Seen INT,
                    street2Seen INT,
                    street3Seen INT,
                    street4Seen INT,
                    sawShowdown INT,
                    street1Aggr INT,
                    street2Aggr INT,
                    street3Aggr INT,
                    street4Aggr INT,
                    otherRaisedStreet0 INT,
                    otherRaisedStreet1 INT,
                    otherRaisedStreet2 INT,
                    otherRaisedStreet3 INT,
                    otherRaisedStreet4 INT,
                    foldToOtherRaisedStreet0 INT,
                    foldToOtherRaisedStreet1 INT,
                    foldToOtherRaisedStreet2 INT,
                    foldToOtherRaisedStreet3 INT,
                    foldToOtherRaisedStreet4 INT,                     
                    wonWhenSeenStreet1 INT,
                    wonWhenSeenStreet2 INT,
                    wonWhenSeenStreet3 INT,
                    wonWhenSeenStreet4 INT,
                    wonAtSD INT,
                    raiseFirstInChance INT,
                    raisedFirstIn INT,
                    foldBbToStealChance INT,
                    foldedBbToSteal INT,
                    foldSbToStealChance INT,
                    foldedSbToSteal INT,
                    street1CBChance INT,
                    street1CBDone INT,
                    street2CBChance INT,
                    street2CBDone INT,
                    street3CBChance INT,
                    street3CBDone INT,
                    street4CBChance INT,
                    street4CBDone INT,
                    foldToStreet1CBChance INT,
                    foldToStreet1CBDone INT,
                    foldToStreet2CBChance INT,
                    foldToStreet2CBDone INT,
                    foldToStreet3CBChance INT,
                    foldToStreet3CBDone INT,
                    foldToStreet4CBChance INT,
                    foldToStreet4CBDone INT,
                    common INT,
                    committed INT,
                    winnings INT,
                    rake INT,
                    rakeDealt decimal,
                    rakeContributed decimal,
                    rakeWeighted decimal,
                    totalProfit INT,
                    allInEV decimal,
                    showdownWinnings INT,
                    nonShowdownWinnings INT,
                    street1CheckCallRaiseChance INT,
                    street1CheckCallDone INT,
                    street1CheckRaiseDone INT,
                    street2CheckCallRaiseChance INT,
                    street2CheckCallDone INT,
                    street2CheckRaiseDone INT,
                    street3CheckCallRaiseChance INT,
                    street3CheckCallDone INT,
                    street3CheckRaiseDone INT,
                    street4CheckCallRaiseChance INT,
                    street4CheckCallDone INT,
                    street4CheckRaiseDone INT,
                    street0Calls INT,
                    street1Calls INT,
                    street2Calls INT,
                    street3Calls INT,
                    street4Calls INT,
                    street0Bets INT,
                    street1Bets INT,
                    street2Bets INT,
                    street3Bets INT,
                    street4Bets INT,
                    street0Raises INT,
                    street1Raises INT,
                    street2Raises INT,
                    street3Raises INT,
                    street4Raises INT,
                    street1Discards INT,
                    street2Discards INT,
                    street3Discards INT)
                    """
            
        self.query['addTourneyIndex'] = """CREATE UNIQUE INDEX siteTourneyNo ON Tourneys (siteTourneyNo, tourneyTypeId)"""

        self.query['addHandsIndex'] = """CREATE UNIQUE INDEX siteHandNo ON Hands (siteHandNo, gametypeId<heroseat>)"""
            
        self.query['addPlayersSeat'] = """CREATE UNIQUE INDEX playerSeat_idx ON HandsPlayers (handId, seatNo)"""
             
        self.query['addHeroSeat'] = """CREATE UNIQUE INDEX heroSeat_idx ON Hands (id, heroSeat)"""
            
        self.query['addHandsPlayersSeat'] = """CREATE UNIQUE INDEX handsPlayerSeat_idx ON Hands (handId, seatNo)"""

        self.query['addPlayersIndex'] = """CREATE UNIQUE INDEX name ON Players (name, siteId)"""

        self.query['addTPlayersIndex'] = """CREATE UNIQUE INDEX tourneyId ON TourneysPlayers (tourneyId, playerId, entryId)"""
            
        self.query['addStartCardsIndex'] = """CREATE UNIQUE INDEX cards_idx ON StartCards (category, rank)"""
            
        self.query['addSeatsIndex'] = """CREATE INDEX seats_idx ON Hands (seats)"""
            
        self.query['addPositionIndex'] = """CREATE INDEX position_idx ON HandsPlayers (position)"""
            
        self.query['addStartCashIndex'] = """CREATE INDEX cash_idx ON HandsPlayers (startCash)"""
            
        self.query['addEffStackIndex'] = """CREATE INDEX eff_stack_idx ON HandsPlayers (effStack)"""
            
        self.query['addTotalProfitIndex'] = """CREATE INDEX profit_idx ON HandsPlayers (totalProfit)"""
            
        self.query['addWinningsIndex'] = """CREATE INDEX winnings_idx ON HandsPlayers (winnings)"""
            
        self.query['addFinalPotIndex'] = """CREATE INDEX pot_idx ON Hands (finalPot)"""
            
        self.query['addStreetIndex'] = """CREATE INDEX street_idx ON HandsStove (streetId, boardId)"""

        self.query['addSessionsCacheCompundIndex'] = """CREATE INDEX SessionsCache_Compound_idx ON SessionsCache(gametypeId, playerId)"""
        self.query['addTourneysCacheCompundIndex'] = """CREATE UNIQUE INDEX TourneysCache_Compound_idx ON TourneysCache(tourneyId, playerId)"""
        self.query['addHudCacheCompundIndex'] = """CREATE UNIQUE INDEX HudCache_Compound_idx ON HudCache(gametypeId, playerId, seats, position, tourneyTypeId, styleKey)"""
        
        self.query['addCardsCacheCompundIndex'] = """CREATE UNIQUE INDEX CardsCache_Compound_idx ON CardsCache(weekId, monthId, gametypeId, tourneyTypeId, playerId, startCards)"""
        self.query['addPositionsCacheCompundIndex'] = """CREATE UNIQUE INDEX PositionsCache_Compound_idx ON PositionsCache(weekId, monthId, gametypeId, tourneyTypeId, playerId, seats, maxPosition, position)"""

        # (left(file, 255)) is not valid syntax on postgres psycopg2 on windows (postgres v8.4)
        # error thrown is HINT:  "No function matches the given name and argument types. You might need to add explicit type casts."
        # so we will just create the index with the full filename.
        self.query['addFilesIndex'] = """CREATE UNIQUE INDEX index_file ON Files (file)"""
            
        self.query['addTableNameIndex'] = """CREATE INDEX index_tableName ON Hands (tableName)"""
        self.query['addPlayerNameIndex'] = """CREATE INDEX index_playerName ON Players (name)"""        
        self.query['addPlayerHeroesIndex'] = """CREATE INDEX player_heroes ON Players (hero)"""
        
        self.query['get_last_hand'] = "select max(id) from Hands"
        
        self.query['get_last_date'] = "SELECT MAX(startTime) FROM Hands"
        
        self.query['get_first_date'] = "SELECT MIN(startTime) FROM Hands"

        self.query['get_player_id'] = """
                select Players.id AS player_id 
                from Players, Sites
                where Players.name = %s
                and Sites.name = %s
                and Players.siteId = Sites.id
            """

        self.query['get_player_names'] = """
                select p.name
                from Players p
                where lower(p.name) like lower(%s)
                and   (p.siteId = %s or %s = -1)
            """

        self.query['get_gameinfo_from_hid'] = """
                SELECT
                        s.name,
                        g.category,
                        g.base,
                        g.type,
                        g.limitType,
                        g.hilo,
                        round(g.smallBlind / 100.0,2),
                        round(g.bigBlind / 100.0,2),
                        round(g.smallBet / 100.0,2),
                        round(g.bigBet / 100.0,2),
                        g.currency,
                        h.gametypeId,
                        g.split
                    FROM
                        Hands as h,
                        Sites as s,
                        Gametypes as g,
                        HandsPlayers as hp,
                        Players as p
                    WHERE
                        h.id = %s
                    and g.id = h.gametypeId
                    and hp.handId = h.id
                    and p.id = hp.playerId
                    and s.id = p.siteId
                    limit 1
            """

        self.query['get_stats_from_hand'] = """
                SELECT hc.playerId                      AS player_id,
                    hp.seatNo                           AS seat,
                    p.name                              AS screen_name,
                    sum(hc.n)                           AS n,
                    sum(hc.street0VPIChance)            AS vpip_opp,
                    sum(hc.street0VPI)                  AS vpip,
                    sum(hc.street0AggrChance)           AS pfr_opp,
                    sum(hc.street0Aggr)                 AS pfr,
                    sum(hc.street0CalledRaiseChance)    AS CAR_opp_0,
                    sum(hc.street0CalledRaiseDone)      AS CAR_0,
                    sum(hc.street0_3BChance)            AS TB_opp_0,
                    sum(hc.street0_3BDone)              AS TB_0,
                    sum(hc.street0_4BChance)            AS FB_opp_0,
                    sum(hc.street0_4BDone)              AS FB_0,
                    sum(hc.street0_C4BChance)           AS CFB_opp_0,
                    sum(hc.street0_C4BDone)             AS CFB_0,
                    sum(hc.street0_FoldTo3BChance)      AS F3B_opp_0,
                    sum(hc.street0_FoldTo3BDone)        AS F3B_0,
                    sum(hc.street0_FoldTo4BChance)      AS F4B_opp_0,
                    sum(hc.street0_FoldTo4BDone)        AS F4B_0,
                    sum(hc.street0_SqueezeChance)       AS SQZ_opp_0,
                    sum(hc.street0_SqueezeDone)         AS SQZ_0,
                    sum(hc.raiseToStealChance)          AS RTS_opp,
                    sum(hc.raiseToStealDone)            AS RTS,
                    sum(hc.success_Steal)               AS SUC_ST,
                    sum(hc.street1Seen)                 AS saw_f,
                    sum(hc.street1Seen)                 AS saw_1,
                    sum(hc.street2Seen)                 AS saw_2,
                    sum(hc.street3Seen)                 AS saw_3,
                    sum(hc.street4Seen)                 AS saw_4,
                    sum(hc.sawShowdown)                 AS sd,
                    sum(hc.street1Aggr)                 AS aggr_1,
                    sum(hc.street2Aggr)                 AS aggr_2,
                    sum(hc.street3Aggr)                 AS aggr_3,
                    sum(hc.street4Aggr)                 AS aggr_4,
                    sum(hc.otherRaisedStreet1)          AS was_raised_1,
                    sum(hc.otherRaisedStreet2)          AS was_raised_2,
                    sum(hc.otherRaisedStreet3)          AS was_raised_3,
                    sum(hc.otherRaisedStreet4)          AS was_raised_4,
                    sum(hc.foldToOtherRaisedStreet1)    AS f_freq_1,
                    sum(hc.foldToOtherRaisedStreet2)    AS f_freq_2,
                    sum(hc.foldToOtherRaisedStreet3)    AS f_freq_3,
                    sum(hc.foldToOtherRaisedStreet4)    AS f_freq_4,
                    sum(hc.wonWhenSeenStreet1)          AS w_w_s_1,
                    sum(hc.wonAtSD)                     AS wmsd,
                    sum(hc.stealChance)                 AS steal_opp,
                    sum(hc.stealDone)                   AS steal,
                    sum(hc.foldSbToStealChance)         AS SBstolen,
                    sum(hc.foldedSbToSteal)             AS SBnotDef,
                    sum(hc.foldBbToStealChance)         AS BBstolen,
                    sum(hc.foldedBbToSteal)             AS BBnotDef,
                    sum(hc.street1CBChance)             AS CB_opp_1,
                    sum(hc.street1CBDone)               AS CB_1,
                    sum(hc.street2CBChance)             AS CB_opp_2,
                    sum(hc.street2CBDone)               AS CB_2,
                    sum(hc.street3CBChance)             AS CB_opp_3,
                    sum(hc.street3CBDone)               AS CB_3,
                    sum(hc.street4CBChance)             AS CB_opp_4,
                    sum(hc.street4CBDone)               AS CB_4,
                    sum(hc.foldToStreet1CBChance)       AS f_cb_opp_1,
                    sum(hc.foldToStreet1CBDone)         AS f_cb_1,
                    sum(hc.foldToStreet2CBChance)       AS f_cb_opp_2,
                    sum(hc.foldToStreet2CBDone)         AS f_cb_2,
                    sum(hc.foldToStreet3CBChance)       AS f_cb_opp_3,
                    sum(hc.foldToStreet3CBDone)         AS f_cb_3,
                    sum(hc.foldToStreet4CBChance)       AS f_cb_opp_4,
                    sum(hc.foldToStreet4CBDone)         AS f_cb_4,
                    sum(hc.totalProfit)                 AS net,
                    sum(gt.bigblind * hc.n)             AS bigblind,
                    sum(hc.street1CheckCallRaiseChance) AS ccr_opp_1,
                    sum(hc.street1CheckCallDone)        AS cc_1,
                    sum(hc.street1CheckRaiseDone)       AS cr_1,
                    sum(hc.street2CheckCallRaiseChance) AS ccr_opp_2,
                    sum(hc.street2CheckCallDone)        AS cc_2,
                    sum(hc.street2CheckRaiseDone)       AS cr_2,
                    sum(hc.street3CheckCallRaiseChance) AS ccr_opp_3,
                    sum(hc.street3CheckCallDone)        AS cc_3,
                    sum(hc.street3CheckRaiseDone)       AS cr_3,
                    sum(hc.street4CheckCallRaiseChance) AS ccr_opp_4,
                    sum(hc.street4CheckCallDone)        AS cc_4
                    sum(hc.street4CheckRaiseDone)       AS cr_4
                    sum(hc.street0Calls)                AS call_0,
                    sum(hc.street1Calls)                AS call_1,
                    sum(hc.street2Calls)                AS call_2,
                    sum(hc.street3Calls)                AS call_3,
                    sum(hc.street4Calls)                AS call_4,
                    sum(hc.street0Bets)                 AS bet_0,
                    sum(hc.street1Bets)                 AS bet_1,
                    sum(hc.street2Bets)                 AS bet_2,
                    sum(hc.street3Bets)                 AS bet_3,
                    sum(hc.street4Bets)                 AS bet_4,
                    sum(hc.street0Raises)               AS raise_0,
                    sum(hc.street1Raises)               AS raise_1,
                    sum(hc.street2Raises)               AS raise_2,
                    sum(hc.street3Raises)               AS raise_3,
                    sum(hc.street4Raises)               AS raise_4
                FROM Hands h
                     INNER JOIN HandsPlayers hp ON (hp.handId = h.id)
                     INNER JOIN HudCache hc ON (    hc.PlayerId = hp.PlayerId+0
                                                AND hc.gametypeId+0 = h.gametypeId+0)
                     INNER JOIN Players p ON (p.id = hp.PlayerId+0)
                     INNER JOIN Gametypes gt ON (gt.id = hc.gametypeId)
                WHERE h.id = %s
                AND   hc.styleKey > %s
                      /* styleKey is currently 'd' (for date) followed by a yyyymmdd
                         date key. Set it to 0000000 or similar to get all records  */
                /* also check activeseats here even if only 3 groups eg 2-3/4-6/7+ 
                   e.g. could use a multiplier:
                   AND   h.seats > X / 1.25  and  hp.seats < X * 1.25
                   where X is the number of active players at the current table (and
                   1.25 would be a config value so user could change it)
                */
                GROUP BY hc.PlayerId, hp.seatNo, p.name
                ORDER BY hc.PlayerId, hp.seatNo, p.name
            """

#    same as above except stats are aggregated for all blind/limit levels
        self.query['get_stats_from_hand_aggregated'] = """
                /* explain query plan */
                SELECT hc.playerId                         AS player_id,
                       max(case when hc.gametypeId = h.gametypeId
                                then hp.seatNo
                                else -1
                           end)                            AS seat,
                       p.name                              AS screen_name,
                       sum(hc.n)                           AS n,
                       sum(hc.street0VPIChance)            AS vpip_opp,
                       sum(hc.street0VPI)                  AS vpip,
                       sum(hc.street0AggrChance)           AS pfr_opp,
                       sum(hc.street0Aggr)                 AS pfr,
                       sum(hc.street0CalledRaiseChance)    AS CAR_opp_0,
                       sum(hc.street0CalledRaiseDone)      AS CAR_0,
                       sum(hc.street0_3BChance)            AS TB_opp_0,
                       sum(hc.street0_3BDone)              AS TB_0,
                       sum(hc.street0_4BChance)            AS FB_opp_0,
                       sum(hc.street0_4BDone)              AS FB_0,
                       sum(hc.street0_C4BChance)           AS CFB_opp_0,
                       sum(hc.street0_C4BDone)             AS CFB_0,
                       sum(hc.street0_FoldTo3BChance)      AS F3B_opp_0,
                       sum(hc.street0_FoldTo3BDone)        AS F3B_0,
                       sum(hc.street0_FoldTo4BChance)      AS F4B_opp_0,
                       sum(hc.street0_FoldTo4BDone)        AS F4B_0,
                       sum(hc.street0_SqueezeChance)       AS SQZ_opp_0,
                       sum(hc.street0_SqueezeDone)         AS SQZ_0,
                       sum(hc.raiseToStealChance)          AS RTS_opp,
                       sum(hc.raiseToStealDone)            AS RTS,
                       sum(hc.success_Steal)               AS SUC_ST,
                       sum(hc.street1Seen)                 AS saw_f,
                       sum(hc.street1Seen)                 AS saw_1,
                       sum(hc.street2Seen)                 AS saw_2,
                       sum(hc.street3Seen)                 AS saw_3,
                       sum(hc.street4Seen)                 AS saw_4,
                       sum(hc.sawShowdown)                 AS sd,
                       sum(hc.street1Aggr)                 AS aggr_1,
                       sum(hc.street2Aggr)                 AS aggr_2,
                       sum(hc.street3Aggr)                 AS aggr_3,
                       sum(hc.street4Aggr)                 AS aggr_4,
                       sum(hc.otherRaisedStreet1)          AS was_raised_1,
                       sum(hc.otherRaisedStreet2)          AS was_raised_2,
                       sum(hc.otherRaisedStreet3)          AS was_raised_3,
                       sum(hc.otherRaisedStreet4)          AS was_raised_4,
                       sum(hc.foldToOtherRaisedStreet1)    AS f_freq_1,
                       sum(hc.foldToOtherRaisedStreet2)    AS f_freq_2,
                       sum(hc.foldToOtherRaisedStreet3)    AS f_freq_3,
                       sum(hc.foldToOtherRaisedStreet4)    AS f_freq_4,
                       sum(hc.wonWhenSeenStreet1)          AS w_w_s_1,
                       sum(hc.wonAtSD)                     AS wmsd,
                       sum(hc.stealChance)                 AS steal_opp,
                       sum(hc.stealDone)                   AS steal,
                       sum(hc.foldSbToStealChance)         AS SBstolen,
                       sum(hc.foldedSbToSteal)             AS SBnotDef,
                       sum(hc.foldBbToStealChance)         AS BBstolen,
                       sum(hc.foldedBbToSteal)             AS BBnotDef,
                       sum(hc.street1CBChance)             AS CB_opp_1,
                       sum(hc.street1CBDone)               AS CB_1,
                       sum(hc.street2CBChance)             AS CB_opp_2,
                       sum(hc.street2CBDone)               AS CB_2,
                       sum(hc.street3CBChance)             AS CB_opp_3,
                       sum(hc.street3CBDone)               AS CB_3,
                       sum(hc.street4CBChance)             AS CB_opp_4,
                       sum(hc.street4CBDone)               AS CB_4,
                       sum(hc.foldToStreet1CBChance)       AS f_cb_opp_1,
                       sum(hc.foldToStreet1CBDone)         AS f_cb_1,
                       sum(hc.foldToStreet2CBChance)       AS f_cb_opp_2,
                       sum(hc.foldToStreet2CBDone)         AS f_cb_2,
                       sum(hc.foldToStreet3CBChance)       AS f_cb_opp_3,
                       sum(hc.foldToStreet3CBDone)         AS f_cb_3,
                       sum(hc.foldToStreet4CBChance)       AS f_cb_opp_4,
                       sum(hc.foldToStreet4CBDone)         AS f_cb_4,
                       sum(hc.totalProfit)                 AS net,
                       sum(gt.bigblind * hc.n)             AS bigblind,
                       sum(hc.street1CheckCallRaiseChance) AS ccr_opp_1,
                       sum(hc.street1CheckCallDone)        AS cc_1,
                       sum(hc.street1CheckRaiseDone)       AS cr_1,
                       sum(hc.street2CheckCallRaiseChance) AS ccr_opp_2,
                       sum(hc.street2CheckCallDone)        AS cc_2,
                       sum(hc.street2CheckRaiseDone)       AS cr_2,
                       sum(hc.street3CheckCallRaiseChance) AS ccr_opp_3,
                       sum(hc.street3CheckCallDone)        AS cc_3,
                       sum(hc.street3CheckRaiseDone)       AS cr_3,
                       sum(hc.street4CheckCallRaiseChance) AS ccr_opp_4,
                       sum(hc.street4CheckCallDone)        AS cc_4,
                       sum(hc.street4CheckRaiseDone)       AS cr_4,
                       sum(hc.street0Calls)                AS call_0,
                       sum(hc.street1Calls)                AS call_1,
                       sum(hc.street2Calls)                AS call_2,
                       sum(hc.street3Calls)                AS call_3,
                       sum(hc.street4Calls)                AS call_4,
                       sum(hc.street0Bets)                 AS bet_0,
                       sum(hc.street1Bets)                 AS bet_1,
                       sum(hc.street2Bets)                 AS bet_2,
                       sum(hc.street3Bets)                 AS bet_3,
                       sum(hc.street4Bets)                 AS bet_4,
                       sum(hc.street0Raises)               AS raise_0,
                       sum(hc.street1Raises)               AS raise_1,
                       sum(hc.street2Raises)               AS raise_2,
                       sum(hc.street3Raises)               AS raise_3,
                       sum(hc.street4Raises)               AS raise_4
                FROM Hands h
                     INNER JOIN HandsPlayers hp ON (hp.handId = h.id)
                     INNER JOIN HudCache hc     ON (hc.playerId = hp.playerId)
                     INNER JOIN Players p       ON (p.id = hc.playerId)
                     INNER JOIN Gametypes gt    ON (gt.id = hc.gametypeId)
                WHERE h.id = %s
                AND   (   /* 2 separate parts for hero and opponents */
                          (    hp.playerId != %s
                           AND hc.styleKey > %s
                           AND hc.gametypeId+0 in
                                 (SELECT gt1.id from Gametypes gt1, Gametypes gt2
                                  WHERE  gt1.siteid = gt2.siteid  /* find gametypes where these match: */
                                  AND    gt1.type = gt2.type               /* ring/tourney */
                                  AND    gt1.category = gt2.category       /* holdem/stud*/
                                  AND    gt1.limittype = gt2.limittype     /* fl/nl */
                                  AND    gt1.bigblind <= gt2.bigblind * %s  /* bigblind similar size */
                                  AND    gt1.bigblind >= gt2.bigblind / %s
                                  AND    gt2.id = %s)
                           AND hc.seats between %s and %s
                          )
                       OR
                          (    hp.playerId = %s
                           AND hc.styleKey > %s
                           AND hc.gametypeId+0 in
                                 (SELECT gt1.id from Gametypes gt1, Gametypes gt2
                                  WHERE  gt1.siteid = gt2.siteid  /* find gametypes where these match: */
                                  AND    gt1.type = gt2.type               /* ring/tourney */
                                  AND    gt1.category = gt2.category       /* holdem/stud*/
                                  AND    gt1.limittype = gt2.limittype     /* fl/nl */
                                  AND    gt1.bigblind <= gt2.bigblind * %s  /* bigblind similar size */
                                  AND    gt1.bigblind >= gt2.bigblind / %s
                                  AND    gt2.id = %s)
                           AND hc.seats between %s and %s
                          )
                      )
                GROUP BY hc.PlayerId, p.name
                ORDER BY hc.PlayerId, p.name
            """
                #  NOTES on above cursor:
                #  - Do NOT include %s inside query in a comment - the db api thinks 
                #  they are actual arguments.
                #  - styleKey is currently 'd' (for date) followed by a yyyymmdd
                #  date key. Set it to 0000000 or similar to get all records
                #  Could also check activeseats here even if only 3 groups eg 2-3/4-6/7+ 
                #  e.g. could use a multiplier:
                #  AND   h.seats > %s / 1.25  and  hp.seats < %s * 1.25
                #  where %s is the number of active players at the current table (and
                #  1.25 would be a config value so user could change it)

        self.query['get_stats_from_hand_session'] = """
                SELECT hp.playerId                                              AS player_id,
                        hp.handId                                                AS hand_id,
                        hp.seatNo                                                AS seat,
                        p.name                                                   AS screen_name,
                        h.seats                                                  AS seats,
                        1                                                        AS n,
                        cast(hp2.street0VPIChance as <signed>integer)            AS vpip_opp,
                        cast(hp2.street0VPI as <signed>integer)                  AS vpip,
                        cast(hp2.street0AggrChance as <signed>integer)           AS pfr_opp,
                        cast(hp2.street0Aggr as <signed>integer)                 AS pfr,
                        cast(hp2.street0CalledRaiseChance as <signed>integer)    AS CAR_opp_0,
                        cast(hp2.street0CalledRaiseDone as <signed>integer)      AS CAR_0,
                        cast(hp2.street0_3BChance as <signed>integer)            AS TB_opp_0,
                        cast(hp2.street0_3BDone as <signed>integer)              AS TB_0,
                        cast(hp2.street0_4BChance as <signed>integer)            AS FB_opp_0,
                        cast(hp2.street0_4BDone as <signed>integer)              AS FB_0,
                        cast(hp2.street0_C4BChance as <signed>integer)           AS CFB_opp_0,
                        cast(hp2.street0_C4BDone as <signed>integer)             AS CFB_0,
                        cast(hp2.street0_FoldTo3BChance as <signed>integer)      AS F3B_opp_0,
                        cast(hp2.street0_FoldTo3BDone as <signed>integer)        AS F3B_0,
                        cast(hp2.street0_FoldTo4BChance as <signed>integer)      AS F4B_opp_0,
                        cast(hp2.street0_FoldTo4BDone as <signed>integer)        AS F4B_0,
                        cast(hp2.street0_SqueezeChance as <signed>integer)       AS SQZ_opp_0,
                        cast(hp2.street0_SqueezeDone as <signed>integer)         AS SQZ_0,
                        cast(hp2.raiseToStealChance as <signed>integer)          AS RTS_opp,
                        cast(hp2.raiseToStealDone as <signed>integer)            AS RTS,
                        cast(hp2.success_Steal as <signed>integer)               AS SUC_ST,
                        cast(hp2.street1Seen as <signed>integer)                 AS saw_f,
                        cast(hp2.street1Seen as <signed>integer)                 AS saw_1,
                        cast(hp2.street2Seen as <signed>integer)                 AS saw_2,
                        cast(hp2.street3Seen as <signed>integer)                 AS saw_3,
                        cast(hp2.street4Seen as <signed>integer)                 AS saw_4,
                        cast(hp2.sawShowdown as <signed>integer)                 AS sd,
                        cast(hp2.street1Aggr as <signed>integer)                 AS aggr_1,
                        cast(hp2.street2Aggr as <signed>integer)                 AS aggr_2,
                        cast(hp2.street3Aggr as <signed>integer)                 AS aggr_3,
                        cast(hp2.street4Aggr as <signed>integer)                 AS aggr_4,
                        cast(hp2.otherRaisedStreet1 as <signed>integer)          AS was_raised_1,
                        cast(hp2.otherRaisedStreet2 as <signed>integer)          AS was_raised_2,
                        cast(hp2.otherRaisedStreet3 as <signed>integer)          AS was_raised_3,
                        cast(hp2.otherRaisedStreet4 as <signed>integer)          AS was_raised_4,
                        cast(hp2.foldToOtherRaisedStreet1 as <signed>integer)    AS f_freq_1,
                        cast(hp2.foldToOtherRaisedStreet2 as <signed>integer)    AS f_freq_2,
                        cast(hp2.foldToOtherRaisedStreet3 as <signed>integer)    AS f_freq_3,
                        cast(hp2.foldToOtherRaisedStreet4 as <signed>integer)    AS f_freq_4,
                        cast(hp2.wonWhenSeenStreet1 as <signed>integer)          AS w_w_s_1,
                        cast(hp2.wonAtSD as <signed>integer)                     AS wmsd,
                        cast(hp2.stealChance as <signed>integer)                 AS steal_opp,
                        cast(hp2.stealDone as <signed>integer)                   AS steal,
                        cast(hp2.foldSbToStealChance as <signed>integer)         AS SBstolen,
                        cast(hp2.foldedSbToSteal as <signed>integer)             AS SBnotDef,
                        cast(hp2.foldBbToStealChance as <signed>integer)         AS BBstolen,
                        cast(hp2.foldedBbToSteal as <signed>integer)             AS BBnotDef,
                        cast(hp2.street1CBChance as <signed>integer)             AS CB_opp_1,
                        cast(hp2.street1CBDone as <signed>integer)               AS CB_1,
                        cast(hp2.street2CBChance as <signed>integer)             AS CB_opp_2,
                        cast(hp2.street2CBDone as <signed>integer)               AS CB_2,
                        cast(hp2.street3CBChance as <signed>integer)             AS CB_opp_3,
                        cast(hp2.street3CBDone as <signed>integer)               AS CB_3,
                        cast(hp2.street4CBChance as <signed>integer)             AS CB_opp_4,
                        cast(hp2.street4CBDone as <signed>integer)               AS CB_4,
                        cast(hp2.foldToStreet1CBChance as <signed>integer)       AS f_cb_opp_1,
                        cast(hp2.foldToStreet1CBDone as <signed>integer)         AS f_cb_1,
                        cast(hp2.foldToStreet2CBChance as <signed>integer)       AS f_cb_opp_2,
                        cast(hp2.foldToStreet2CBDone as <signed>integer)         AS f_cb_2,
                        cast(hp2.foldToStreet3CBChance as <signed>integer)       AS f_cb_opp_3,
                        cast(hp2.foldToStreet3CBDone as <signed>integer)         AS f_cb_3,
                        cast(hp2.foldToStreet4CBChance as <signed>integer)       AS f_cb_opp_4,
                        cast(hp2.foldToStreet4CBDone as <signed>integer)         AS f_cb_4,
                        cast(hp2.totalProfit as <signed>integer)                 AS net,
                        cast(gt.bigblind as <signed>integer)                     AS bigblind,
                        cast(hp2.street1CheckCallRaiseChance as <signed>integer) AS ccr_opp_1,
                        cast(hp2.street1CheckCallDone as <signed>integer)        AS cc_1,
                        cast(hp2.street1CheckRaiseDone as <signed>integer)       AS cr_1,
                        cast(hp2.street2CheckCallRaiseChance as <signed>integer) AS ccr_opp_2,
                        cast(hp2.street2CheckCallDone as <signed>integer)        AS cc_2,
                        cast(hp2.street2CheckRaiseDone as <signed>integer)       AS cr_2,
                        cast(hp2.street3CheckCallRaiseChance as <signed>integer) AS ccr_opp_3,
                        cast(hp2.street3CheckCallDone as <signed>integer)        AS cc_3,
                        cast(hp2.street3CheckRaiseDone as <signed>integer)       AS cr_3,
                        cast(hp2.street4CheckCallRaiseChance as <signed>integer) AS ccr_opp_4,
                        cast(hp2.street4CheckCallDone as <signed>integer)        AS cc_4,
                        cast(hp2.street4CheckRaiseDone as <signed>integer)       AS cr_4,
                        cast(hp2.street0Calls as <signed>integer)                AS call_0,
                        cast(hp2.street1Calls as <signed>integer)                AS call_1,
                        cast(hp2.street2Calls as <signed>integer)                AS call_2,
                        cast(hp2.street3Calls as <signed>integer)                AS call_3,
                        cast(hp2.street4Calls as <signed>integer)                AS call_4,
                        cast(hp2.street0Bets as <signed>integer)                 AS bet_0,
                        cast(hp2.street1Bets as <signed>integer)                 AS bet_1,
                        cast(hp2.street2Bets as <signed>integer)                 AS bet_2,
                        cast(hp2.street3Bets as <signed>integer)                 AS bet_3,
                        cast(hp2.street4Bets as <signed>integer)                 AS bet_4,
                        cast(hp2.street0Raises as <signed>integer)               AS raise_0,
                        cast(hp2.street1Raises as <signed>integer)               AS raise_1,
                        cast(hp2.street2Raises as <signed>integer)               AS raise_2,
                        cast(hp2.street3Raises as <signed>integer)               AS raise_3,
                        cast(hp2.street4Raises as <signed>integer)               AS raise_4
                        FROM Hands h                                                  /* this hand */
                        INNER JOIN Hands h2         ON (    h2.id >= %s           /* other hands */
                                                        AND h2.tableName = h.tableName)
                        INNER JOIN HandsPlayers hp  ON (h.id = hp.handId)        /* players in this hand */
                        INNER JOIN HandsPlayers hp2 ON (    hp2.playerId+0 = hp.playerId+0
                                                        AND hp2.handId = h2.id)  /* other hands by these players */
                        INNER JOIN Players p        ON (p.id = hp2.PlayerId+0)
                        INNER JOIN Gametypes gt     ON (gt.id = h2.gametypeId)
                WHERE h.id = %s
                /* check activeseats once this data returned (don't want to do that here as it might
                    assume a session ended just because the number of seats dipped for a few hands)
                */
                AND   (   /* 2 separate parts for hero and opponents */
                            (    hp2.playerId != %s
                            AND h2.seats between %s and %s
                            )
                        OR
                            (    hp2.playerId = %s
                            AND h2.seats between %s and %s
                            )
                        )
                ORDER BY h.startTime desc, hp2.PlayerId
                /* order rows by handstart descending so that we can stop reading rows when
                    there's a gap over X minutes between hands (ie. when we get back to start of
                    the session */
            """
     
        self.query['get_players_from_hand'] = """
                SELECT HandsPlayers.playerId, seatNo, name
                FROM  HandsPlayers INNER JOIN Players ON (HandsPlayers.playerId = Players.id)
                WHERE handId = %s
            """
#                    WHERE handId = %s AND Players.id LIKE %s

        self.query['get_winners_from_hand'] = """
                SELECT name, winnings
                FROM HandsPlayers, Players
                WHERE winnings > 0
                    AND Players.id = HandsPlayers.playerId
                    AND handId = %s;
            """

        self.query['get_table_name'] = """
                SELECT h.tableName, gt.maxSeats, gt.category, gt.type, gt.fast, s.id, s.name
                     , count(1) as numseats
                FROM Hands h, Gametypes gt, Sites s, HandsPlayers hp
                WHERE h.id = %s
                    AND   gt.id = h.gametypeId
                    AND   s.id = gt.siteID
                    AND   hp.handId = h.id
                GROUP BY h.tableName, gt.maxSeats, gt.category, gt.type, gt.fast, s.id, s.name
            """

        self.query['get_actual_seat'] = """
                select seatNo
                from HandsPlayers
                where HandsPlayers.handId = %s
                and   HandsPlayers.playerId  = (select Players.id from Players
                                                where Players.name = %s)
            """

        self.query['get_cards'] = """
/*
    changed to activate mucked card display in draw games
    in draw games, card6->card20 contain 3 sets of 5 cards at each draw

    CASE code searches from the highest card number (latest draw) and when
    it finds a non-zero card, it returns that set of data
*/
            SELECT
                seatNo AS seat_number,
                CASE Gametypes.base
                    when 'draw' then COALESCE(NULLIF(card16,0), NULLIF(card11,0), NULLIF(card6,0), card1)
                    else card1
                end card1,
                CASE Gametypes.base
                    when 'draw' then COALESCE(NULLIF(card17,0), NULLIF(card12,0), NULLIF(card7,0), card2)
                    else card2
                end card2,
                CASE Gametypes.base
                    when 'draw' then COALESCE(NULLIF(card18,0), NULLIF(card13,0), NULLIF(card8,0), card3)
                    else card3
                end card3,
                CASE Gametypes.base
                    when 'draw' then COALESCE(NULLIF(card19,0), NULLIF(card14,0), NULLIF(card9,0), card4)
                    else card4
                end card4,
                CASE Gametypes.base
                    when 'draw' then COALESCE(NULLIF(card20,0), NULLIF(card15,0), NULLIF(card10,0), card5)
                    else card5
                end card5,
                CASE Gametypes.base
                    when 'draw' then 0
                    else card6
                end card6,
                CASE Gametypes.base
                    when 'draw' then 0
                    else card7
                end card7

                FROM HandsPlayers, Hands, Gametypes
                WHERE handID = %s
                 AND HandsPlayers.handId=Hands.id
                 AND Hands.gametypeId = Gametypes.id
                ORDER BY seatNo
            """

        self.query['get_common_cards'] = """
                select
                boardcard1,
                boardcard2,
                boardcard3,
                boardcard4,
                boardcard5
                from Hands
                where Id = %s
            """

        self.query['get_hand_1day_ago'] = """
            select coalesce(max(id),0)
            from Hands
            where startTime < datetime(strftime('%J', 'now') - 1)"""

        # not used yet ...
        # gets a date, would need to use handsplayers (not hudcache) to get exact hand Id
        self.query['get_date_nhands_ago'] = """
            select 'd' || strftime(max(h3.startTime), 'YYMMDD')
            from (select hp.playerId
                        ,coalesce(greatest(max(hp.handId)-%s,1),1) as maxminusx
                    from HandsPlayers hp
                    where hp.playerId = %s
                    group by hp.playerId) hp2
            inner join HandsPlayers hp3 on (    hp3.handId <= hp2.maxminusx
                                            and hp3.playerId = hp2.playerId)
            inner join Hands h          on (h.id = hp3.handId)"""

        # Used in *Filters:
        #self.query['getLimits'] = already defined further up
        self.query['getLimits2'] = """SELECT DISTINCT type, limitType, bigBlind 
                                      from Gametypes
                                      ORDER by type, limitType DESC, bigBlind DESC"""
        self.query['getLimits3'] = """select DISTINCT type
                                           , gt.limitType
                                           , case type
                                                 when 'ring' then bigBlind 
-                                                else buyin
-                                            end as bb_or_buyin
                                      from Gametypes gt
                                      cross join TourneyTypes tt
                                      order by type, gt.limitType DESC, bb_or_buyin DESC"""
#         self.query['getCashLimits'] = """select DISTINCT type
#                                            , limitType
#                                            , bigBlind as bb_or_buyin
#                                       from Gametypes gt
#                                       WHERE type = 'ring'
#                                       order by type, limitType DESC, bb_or_buyin DESC"""

        self.query['getCashLimits'] = """select DISTINCT type
                                           , limitType
                                           , bigBlind as bb_or_buyin
                                      from Gametypes gt
                                      WHERE type = 'ring'
                                      order by type, limitType DESC, bb_or_buyin DESC"""
                                      
        self.query['getPositions'] = """select distinct position
                                      from HandsPlayers gt
                                      order by position"""
                                      
        #FIXME: Some stats not added to DetailedStats (miss raise to steal)
        self.query['playerDetailedStats'] = """
                    select  <hgametypeId>                                                          AS hgametypeid
                        ,<playerName>                                                           AS pname
                        ,gt.base
                        ,gt.category                                                            AS category
                        ,upper(gt.limitType)                                                    AS limittype
                        ,s.name                                                                 AS name
                        ,min(gt.bigBlind)                                                       AS minbigblind
                        ,max(gt.bigBlind)                                                       AS maxbigblind
                        ,gt.ante                                                                AS ante
                        ,gt.currency                                                            AS currency
                        /*,<hcgametypeId>                                                       AS gtid*/
                        ,<position>                                                             AS plposition
                        ,gt.fast                                                                AS fast
                        ,count(1)                                                               AS n
                        ,case when sum(cast(hp.street0VPIChance as <signed>integer)) = 0 then -999
                                else 100.0*sum(cast(hp.street0VPI as <signed>integer))/sum(cast(hp.street0VPIChance as <signed>integer))
                            end                                                                    AS vpip
                        ,case when sum(cast(hp.street0AggrChance as <signed>integer)) = 0 then -999
                                else 100.0*sum(cast(hp.street0Aggr as <signed>integer))/sum(cast(hp.street0AggrChance as <signed>integer))
                            end                                                                    AS pfr
                        ,case when sum(cast(hp.street0CalledRaiseChance as <signed>integer)) = 0 then -999
                                else 100.0*sum(cast(hp.street0CalledRaiseDone as <signed>integer))/sum(cast(hp.street0CalledRaiseChance as <signed>integer))
                            end                                                                    AS car0
                        ,case when sum(cast(hp.street0_3Bchance as <signed>integer)) = 0 then -999
                                else 100.0*sum(cast(hp.street0_3Bdone as <signed>integer))/sum(cast(hp.street0_3Bchance as <signed>integer))
                            end                                                                    AS pf3
                        ,case when sum(cast(hp.street0_4Bchance as <signed>integer)) = 0 then -999
                                else 100.0*sum(cast(hp.street0_4Bdone as <signed>integer))/sum(cast(hp.street0_4Bchance as <signed>integer))
                            end                                                                    AS pf4
                        ,case when sum(cast(hp.street0_FoldTo3Bchance as <signed>integer)) = 0 then -999
                                else 100.0*sum(cast(hp.street0_FoldTo3Bdone as <signed>integer))/sum(cast(hp.street0_FoldTo3Bchance as <signed>integer))
                            end                                                                    AS pff3
                        ,case when sum(cast(hp.street0_FoldTo4Bchance as <signed>integer)) = 0 then -999
                                else 100.0*sum(cast(hp.street0_FoldTo4Bdone as <signed>integer))/sum(cast(hp.street0_FoldTo4Bchance as <signed>integer))
                            end                                                                    AS pff4
                        ,case when sum(cast(hp.raiseFirstInChance as <signed>integer)) = 0 then -999
                                else 100.0 * sum(cast(hp.raisedFirstIn as <signed>integer)) / 
                                    sum(cast(hp.raiseFirstInChance as <signed>integer))
                            end                                                                    AS rfi
                        ,case when sum(cast(hp.stealChance as <signed>integer)) = 0 then -999
                                else 100.0 * sum(cast(hp.stealDone as <signed>integer)) / 
                                    sum(cast(hp.stealChance as <signed>integer))
                            end                                                                    AS steals
                        ,case when sum(cast(hp.stealDone as <signed>integer)) = 0 then -999
                                else 100.0 * sum(cast(hp.success_Steal as <signed>integer)) / 
                                    sum(cast(hp.stealDone as <signed>integer))
                            end                                                                    AS suc_steal
                        ,100.0*sum(cast(hp.street1Seen as <signed>integer))/count(1)            AS saw_f
                        ,100.0*sum(cast(hp.sawShowdown as <signed>integer))/count(1)            AS sawsd
                        ,case when sum(cast(hp.street1Seen as <signed>integer)) = 0 then -999
                                else 100.0*sum(cast(hp.wonWhenSeenStreet1 as <signed>integer))/sum(cast(hp.street1Seen as <signed>integer))
                            end                                                                    AS wmsf
                        ,case when sum(cast(hp.street1Seen as <signed>integer)) = 0 then -999
                                else 100.0*sum(cast(hp.sawShowdown as <signed>integer))/sum(cast(hp.street1Seen as <signed>integer))
                            end                                                                    AS wtsdwsf
                        ,case when sum(cast(hp.sawShowdown as <signed>integer)) = 0 then -999
                                else 100.0*sum(cast(hp.wonAtSD as <signed>integer))/sum(cast(hp.sawShowdown as <signed>integer))
                            end                                                                    AS wmsd
                        ,case when sum(cast(hp.street1Seen as <signed>integer)) = 0 then -999
                                else 100.0*sum(cast(hp.street1Aggr as <signed>integer))/sum(cast(hp.street1Seen as <signed>integer))
                            end                                                                    AS flafq
                        ,case when sum(cast(hp.street2Seen as <signed>integer)) = 0 then -999
                                else 100.0*sum(cast(hp.street2Aggr as <signed>integer))/sum(cast(hp.street2Seen as <signed>integer))
                            end                                                                    AS tuafq
                        ,case when sum(cast(hp.street3Seen as <signed>integer)) = 0 then -999
                                else 100.0*sum(cast(hp.street3Aggr as <signed>integer))/sum(cast(hp.street3Seen as <signed>integer))
                            end                                                                    AS rvafq
                        ,case when sum(cast(hp.street1Seen as <signed>integer))+sum(cast(hp.street2Seen as <signed>integer))+sum(cast(hp.street3Seen as <signed>integer)) = 0 then -999
                                else 100.0*(sum(cast(hp.street1Aggr as <signed>integer))+sum(cast(hp.street2Aggr as <signed>integer))+sum(cast(hp.street3Aggr as <signed>integer)))
                                        /(sum(cast(hp.street1Seen as <signed>integer))+sum(cast(hp.street2Seen as <signed>integer))+sum(cast(hp.street3Seen as <signed>integer)))
                            end                                                                    AS pofafq
                        ,case when sum(cast(hp.street1Calls as <signed>integer))+ sum(cast(hp.street2Calls as <signed>integer))+ sum(cast(hp.street3Calls as <signed>integer))+ sum(cast(hp.street4Calls as <signed>integer)) = 0 then -999
                                else (sum(cast(hp.street1Aggr as <signed>integer)) + sum(cast(hp.street2Aggr as <signed>integer)) + sum(cast(hp.street3Aggr as <signed>integer)) + sum(cast(hp.street4Aggr as <signed>integer)))
                                    /(0.0+sum(cast(hp.street1Calls as <signed>integer))+ sum(cast(hp.street2Calls as <signed>integer))+ sum(cast(hp.street3Calls as <signed>integer))+ sum(cast(hp.street4Calls as <signed>integer)))
                            end                                                                    AS aggfac
                        ,100.0*(sum(cast(hp.street1Aggr as <signed>integer)) + sum(cast(hp.street2Aggr as <signed>integer)) + sum(cast(hp.street3Aggr as <signed>integer)) + sum(cast(hp.street4Aggr as <signed>integer))) 
                                    / ((sum(cast(hp.foldToOtherRaisedStreet1 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet2 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet3 as <signed>integer))+ sum(cast(hp.foldToOtherRaisedStreet4 as <signed>integer))) +
                                    (sum(cast(hp.street1Calls as <signed>integer))+ sum(cast(hp.street2Calls as <signed>integer))+ sum(cast(hp.street3Calls as <signed>integer))+ sum(cast(hp.street4Calls as <signed>integer))) +
                                    (sum(cast(hp.street1Aggr as <signed>integer)) + sum(cast(hp.street2Aggr as <signed>integer)) + sum(cast(hp.street3Aggr as <signed>integer)) + sum(cast(hp.street4Aggr as <signed>integer))) )
                                                                                                AS aggfrq
                        ,100.0*(sum(cast(hp.street1CBDone as <signed>integer)) + sum(cast(hp.street2CBDone as <signed>integer)) + sum(cast(hp.street3CBDone as <signed>integer)) + sum(cast(hp.street4CBDone as <signed>integer))) 
                                    / (sum(cast(hp.street1CBChance as <signed>integer))+ sum(cast(hp.street2CBChance as <signed>integer))+ sum(cast(hp.street3CBChance as <signed>integer))+ sum(cast(hp.street4CBChance as <signed>integer))) 
                                                                                                AS conbet
                        ,sum(hp.totalProfit)/100.0                                              AS net
                        ,sum(hp.rake)/100.0                                                     AS rake
                        ,100.0*avg(hp.totalProfit/(gt.bigBlind+0.0))                            AS bbper100
                        ,avg(hp.totalProfit)/100.0                                              AS profitperhand
                        ,100.0*avg((hp.totalProfit+hp.rake)/(gt.bigBlind+0.0))                  AS bb100xr
                        ,avg((hp.totalProfit+hp.rake)/100.0)                                    AS profhndxr
                        ,avg(h.seats+0.0)                                                       AS avgseats
                        ,variance(hp.totalProfit/100.0)                                         AS variance
                        ,sqrt(variance(hp.totalProfit/100.0))                                                         AS stddev
                    from HandsPlayers hp
                        inner join Hands h       on  (h.id = hp.handId)
                        inner join Gametypes gt  on  (gt.Id = h.gametypeId)
                        inner join Sites s       on  (s.Id = gt.siteId)
                        inner join Players p     on  (p.Id = hp.playerId)
                    where hp.playerId in <player_test>
                    <game_test>
                    <site_test>
                    <currency_test>
                    /*and   hp.tourneysPlayersId IS NULL*/
                    and   h.seats <seats_test>
                    <flagtest>
                    <cardstest>
                    <gtbigBlind_test>
                    and   datetime(h.startTime) <datestest>
                    group by hgametypeId
                            ,hp.playerId
                            ,gt.base
                            ,gt.category
                            <groupbyseats>
                            ,plposition
                            ,upper(gt.limitType)
                            ,gt.fast
                            ,s.name
                    having 1 = 1 <havingclause>
                    order by hp.playerId
                            ,gt.base
                            ,gt.category
                            <orderbyseats>
                            ,case <position> when 'B' then 'B'
                                            when 'S' then 'S'
                                            when '0' then 'Y'
                                            else 'Z'||<position>
                            end
                            <orderbyhgametypeId>
                            ,upper(gt.limitType) desc
                            ,max(gt.bigBlind) desc
                            ,gt.fast
                            ,s.name"""

        #FIXME: 3/4bet and foldTo don't added four tournaments yet
        self.query['tourneyPlayerDetailedStats'] = """
                    select s.name                                                                 AS siteName
                        ,tt.currency                                                            AS currency
                        ,(CASE
                            WHEN tt.currency = 'play' THEN tt.buyIn
                            ELSE tt.buyIn/100.0
                            END)                                                                  AS buyIn
                        ,tt.fee/100.0                                                           AS fee
                        ,tt.category                                                            AS category
                        ,tt.limitType                                                           AS limitType
                        ,tt.speed                                                                AS speed
                        ,tt.maxSeats                                                            AS maxSeats
						,tt.knockout                                                            AS knockout
						,tt.reEntry                                                             AS reEntry
                        ,p.name                                                                 AS playerName
                        ,COUNT(1)                                                               AS tourneyCount
                        ,SUM(CASE WHEN tp.rank > 0 THEN 0 ELSE 1 END)                           AS unknownRank
                        ,(CAST(SUM(CASE WHEN winnings > 0 THEN 1 ELSE 0 END) AS REAL)/CAST(COUNT(1) AS REAL))*100                 AS itm
                        ,SUM(CASE WHEN rank = 1 THEN 1 ELSE 0 END)                              AS _1st
                        ,SUM(CASE WHEN rank = 2 THEN 1 ELSE 0 END)                              AS _2nd
                        ,SUM(CASE WHEN rank = 3 THEN 1 ELSE 0 END)                              AS _3rd
                        ,SUM(tp.winnings+COALESCE(tp.koCount*tt.koBounty,0))/100.0              AS won
                        ,SUM(CASE
                                WHEN tt.currency = 'play' THEN tt.buyIn
                                ELSE (tt.buyIn+tt.fee)/100.0
                                END)                                                               AS spent
                        ,SUM(tp.winnings+COALESCE(tp.koCount*tt.koBounty,0)-tt.buyIn-tt.fee)/100.0	 								AS net
                        ,(CAST(SUM(tp.winnings+COALESCE(tp.koCount*tt.koBounty,0) - tt.buyin - tt.fee) AS REAL)/
                            CAST(SUM(tt.buyin+tt.fee) AS REAL))* 100.0                                                                    AS roi
                        ,SUM(tp.winnings+COALESCE(tp.koCount*tt.koBounty,0)-(tt.buyin+tt.fee))/100.0/(COUNT(1)-SUM(CASE WHEN tp.rank > 0 THEN 0 ELSE 1 END)) AS profitPerTourney
                    from TourneysPlayers tp
                        inner join Tourneys t        on  (t.id = tp.tourneyId)
                        inner join TourneyTypes tt   on  (tt.Id = t.tourneyTypeId)
                        inner join Sites s           on  (s.Id = tt.siteId)
                        inner join Players p         on  (p.Id = tp.playerId)
                    where tp.playerId in <nametest> <sitetest>
                    AND   ((t.startTime > '<startdate_test>' AND t.startTime < '<enddate_test>')
                                    OR t.startTime is NULL)
                    group by tourneyTypeId, playerName
                    order by tourneyTypeId
                            ,playerName
                            ,siteName"""

        self.query['playerStats'] = """
            SELECT
                    upper(substr(stats.category,1,1)) || substr(stats.category,2) || ' ' ||
                    stats.name || ' ' ||
                    cast(stats.bigBlindDesc as char) || ' ' || stats.maxSeats || ' seat'  AS Game
                    ,stats.n,stats.vpip,stats.pfr,stats.pf3,stats.pf4,stats.pff3,stats.pff4
                    ,stats.steals,stats.saw_f,stats.sawsd,stats.wtsdwsf,stats.wmsd,stats.FlAFq
                    ,stats.TuAFq,stats.RvAFq,stats.PoFAFq,stats.Net,stats.BBper100,stats.Profitperhand
                    ,case when hprof2.variance = -999 then '-' else round(hprof2.variance, 2)
                    end                                                                   AS Variance
                    ,case when hprof2.stddev = -999 then '-' else round(hprof2.stddev, 2)
                    end                                                                   AS Stddev
                    ,stats.AvgSeats
            FROM
                (select /* stats from hudcache */
                        gt.base
                        ,gt.category,maxSeats,gt.bigBlind,gt.currency
                        ,upper(gt.limitType)                                             AS limitType
                        ,s.name
                        ,<selectgt.bigBlind>                                             AS bigBlindDesc
                        ,<hcgametypeId>                                                  AS gtId
                        ,sum(n)                                                          AS n
                        ,case when sum(street0VPIChance) = 0 then '0'
                                else round(100.0*sum(street0VPI)/sum(street0VPIChance),1)
                        end                                                             AS vpip
                        ,case when sum(street0AggrChance) = 0 then '0'
                                else round(100.0*sum(street0Aggr)/sum(street0AggrChance),1)
                        end                                                             AS pfr
                        ,case when sum(street0CalledRaiseChance) = 0 then '0'
                                else round(100.0*sum(street0CalledRaiseDone)/sum(street0CalledRaiseChance),1)
                        end                                                             AS car0
                        ,case when sum(street0_3Bchance) = 0 then '0'
                                else round(100.0*sum(street0_3Bdone)/sum(street0_3Bchance),1)
                        end                                                             AS pf3
                        ,case when sum(street0_4Bchance) = 0 then '0'
                                else round(100.0*sum(street0_4Bdone)/sum(street0_4Bchance),1)
                        end                                                             AS pf4
                        ,case when sum(street0_FoldTo3Bchance) = 0 then '0'
                                else round(100.0*sum(street0_FoldTo3Bdone)/sum(street0_FoldTo3Bchance),1)
                        end                                                             AS pff3
                        ,case when sum(street0_FoldTo4Bchance) = 0 then '0'
                                else round(100.0*sum(street0_FoldTo4Bdone)/sum(street0_FoldTo4Bchance),1)
                        end                                                             AS pff4
                        ,case when sum(raiseFirstInChance) = 0 then '-'
                                else round(100.0*sum(raisedFirstIn)/sum(raiseFirstInChance),1)
                        end                                                             AS steals
                        ,round(100.0*sum(street1Seen)/sum(n),1)                          AS saw_f
                        ,round(100.0*sum(sawShowdown)/sum(n),1)                          AS sawsd
                        ,case when sum(street1Seen) = 0 then '-'
                                else round(100.0*sum(sawShowdown)/sum(street1Seen),1)
                        end                                                             AS wtsdwsf
                        ,case when sum(sawShowdown) = 0 then '-'
                                else round(100.0*sum(wonAtSD)/sum(sawShowdown),1)
                        end                                                             AS wmsd
                        ,case when sum(street1Seen) = 0 then '-'
                                else round(100.0*sum(street1Aggr)/sum(street1Seen),1)
                        end                                                             AS FlAFq
                        ,case when sum(street2Seen) = 0 then '-'
                                else round(100.0*sum(street2Aggr)/sum(street2Seen),1)
                        end                                                             AS TuAFq
                        ,case when sum(street3Seen) = 0 then '-'
                            else round(100.0*sum(street3Aggr)/sum(street3Seen),1)
                        end                                                             AS RvAFq
                        ,case when sum(street1Seen)+sum(street2Seen)+sum(street3Seen) = 0 then '-'
                            else round(100.0*(sum(street1Aggr)+sum(street2Aggr)+sum(street3Aggr))
                                        /(sum(street1Seen)+sum(street2Seen)+sum(street3Seen)),1)
                        end                                                             AS PoFAFq
                        ,round(sum(totalProfit)/100.0,2)                                 AS Net
                        ,round((sum(totalProfit/(gt.bigBlind+0.0))) / (sum(n)/100.0),2)
                                                                                        AS BBper100
                        ,round( (sum(totalProfit)/100.0) / sum(n), 4)                    AS Profitperhand
                        ,round( sum(seats*n)/(sum(n)+0.0), 2)                            AS AvgSeats
                    from Gametypes gt
                        inner join Sites s on s.Id = gt.siteId
                        inner join HudCache hc on hc.gametypeId = gt.Id
                    where hc.playerId in <player_test>
                    <gtbigBlind_test>
                    and   hc.seats <seats_test>
                    and   '20' || substr(hc.styleKey,2,2) || '-' || substr(hc.styleKey,4,2) || '-' ||
                                substr(hc.styleKey,6,2) <datestest>
                    group by gt.base,gt.category,upper(gt.limitType),s.name <groupbygt.bigBlind>,gtId
                ) stats
            inner join
                ( select /* profit from handsplayers/handsactions */
                            hprof.gtId, sum(hprof.profit) sum_profit,
                            avg(hprof.profit/100.0) profitperhand,
                            case when hprof.gtId = -1 then -999
                                else variance(hprof.profit/100.0)
                            end as variance
                            ,case when hprof.gtId = -1 then -999
                                else sqrt(variance(hprof.profit/100.0))
                            end as stddev
                    from
                        (select hp.handId, <hgametypeId> as gtId, hp.totalProfit as profit
                        from HandsPlayers hp
                        inner join Hands h        ON h.id            = hp.handId
                        where hp.playerId in <player_test>
                        and   hp.tourneysPlayersId IS NULL
                        and   datetime(h.startTime) <datestest>
                        group by hp.handId, gtId, hp.totalProfit
                        ) hprof
                    group by hprof.gtId
                    ) hprof2
                on hprof2.gtId = stats.gtId
            order by stats.category, stats.bigBlind, stats.limittype, stats.currency, stats.maxSeats <orderbyseats>"""

        self.query['playerStatsByPosition'] = """
            SELECT
                    upper(substr(stats.category,1,1)) || substr(stats.category,2) || ' ' ||
                    stats.name || ' ' ||
                    cast(stats.bigBlindDesc as char) || ' ' || stats.maxSeats || ' seat'  AS Game
                    ,case when stats.PlPosition = -2 then 'BB'
                        when stats.PlPosition = -1 then 'SB'
                        when stats.PlPosition =  0 then 'Btn'
                        when stats.PlPosition =  1 then 'CO'
                        when stats.PlPosition =  2 then 'MP'
                        when stats.PlPosition =  5 then 'EP'
                        else 'xx'
                    end                                                                   AS PlPosition
                    ,stats.n,stats.vpip,stats.pfr,stats.pf3,stats.pf4,stats.pff3,stats.pff4
                    ,stats.steals,stats.saw_f,stats.sawsd,stats.wtsdwsf,stats.wmsd,stats.FlAFq
                    ,stats.TuAFq,stats.RvAFq,stats.PoFAFq,stats.Net,stats.BBper100,stats.Profitperhand
                    ,case when hprof2.variance = -999 then '-'
                        else round(hprof2.variance, 2)
                    end                                                                   AS Variance
                    ,case when hprof2.variance = -999 then '-'
                        else round(hprof2.stddev, 2)
                    end                                                                   AS Stddev
                    ,stats.AvgSeats
            FROM
                (select /* stats from hudcache */
                        gt.base
                        ,gt.category,maxSeats,gt.bigBlind,gt.currency
                        ,upper(gt.limitType)                                             AS limitType
                        ,s.name
                        ,<selectgt.bigBlind>                                             AS bigBlindDesc
                        ,<hcgametypeId>                                                  AS gtId
                        ,case when hc.position = 'B' then -2
                                when hc.position = 'S' then -1
                                when hc.position = 'D' then  0
                                when hc.position = 'C' then  1
                                when hc.position = 'M' then  2
                                when hc.position = 'E' then  5
                                else 9
                        end                                                             AS PlPosition
                        ,sum(n)                                                          AS n
                        ,case when sum(street0VPIChance) = 0 then '0'
                                else round(100.0*sum(street0VPI)/sum(street0VPIChance),1)
                        end                                                             AS vpip
                        ,case when sum(street0AggrChance) = 0 then '0'
                                else round(100.0*sum(street0Aggr)/sum(street0AggrChance),1)
                        end                                                             AS pfr
                        ,case when sum(street0CalledRaiseChance) = 0 then '0'
                                else round(100.0*sum(street0CalledRaiseDone)/sum(street0CalledRaiseChance),1)
                        end                                                             AS car0
                        ,case when sum(street0_3Bchance) = 0 then '0'
                                else round(100.0*sum(street0_3Bdone)/sum(street0_3Bchance),1)
                        end                                                             AS pf3
                        ,case when sum(street0_4Bchance) = 0 then '0'
                                else round(100.0*sum(street0_4Bdone)/sum(street0_4Bchance),1)
                        end                                                             AS pf4
                        ,case when sum(street0_FoldTo3Bchance) = 0 then '0'
                                else round(100.0*sum(street0_FoldTo3Bdone)/sum(street0_FoldTo3Bchance),1)
                        end                                                             AS pff3
                        ,case when sum(street0_FoldTo4Bchance) = 0 then '0'
                                else round(100.0*sum(street0_FoldTo4Bdone)/sum(street0_FoldTo4Bchance),1)
                        end                                                             AS pff4
                        ,case when sum(raiseFirstInChance) = 0 then '-'
                                else round(100.0*sum(raisedFirstIn)/sum(raiseFirstInChance),1)
                        end                                                             AS steals
                        ,round(100.0*sum(street1Seen)/sum(n),1)                          AS saw_f
                        ,round(100.0*sum(sawShowdown)/sum(n),1)                          AS sawsd
                        ,case when sum(street1Seen) = 0 then '-'
                                else round(100.0*sum(sawShowdown)/sum(street1Seen),1)
                        end                                                             AS wtsdwsf
                        ,case when sum(sawShowdown) = 0 then '-'
                                else round(100.0*sum(wonAtSD)/sum(sawShowdown),1)
                        end                                                             AS wmsd
                        ,case when sum(street1Seen) = 0 then '-'
                                else round(100.0*sum(street1Aggr)/sum(street1Seen),1)
                        end                                                             AS FlAFq
                        ,case when sum(street2Seen) = 0 then '-'
                                else round(100.0*sum(street2Aggr)/sum(street2Seen),1)
                        end                                                             AS TuAFq
                        ,case when sum(street3Seen) = 0 then '-'
                            else round(100.0*sum(street3Aggr)/sum(street3Seen),1)
                        end                                                             AS RvAFq
                        ,case when sum(street1Seen)+sum(street2Seen)+sum(street3Seen) = 0 then '-'
                            else round(100.0*(sum(street1Aggr)+sum(street2Aggr)+sum(street3Aggr))
                                        /(sum(street1Seen)+sum(street2Seen)+sum(street3Seen)),1)
                        end                                                             AS PoFAFq
                        ,round(sum(totalProfit)/100.0,2)                                 AS Net
                        ,round((sum(totalProfit/(gt.bigBlind+0.0))) / (sum(n)/100.0),2)
                                                                                        AS BBper100
                        ,round( (sum(totalProfit)/100.0) / sum(n), 4)                    AS Profitperhand
                        ,round( sum(seats*n)/(sum(n)+0.0), 2)                            AS AvgSeats
                    from Gametypes gt
                        inner join Sites s on s.Id = gt.siteId
                        inner join HudCache hc on hc.gametypeId = gt.Id
                    where hc.playerId in <player_test>
                    <gtbigBlind_test>
                    and   hc.seats <seats_test>
                    and   '20' || substr(hc.styleKey,2,2) || '-' || substr(hc.styleKey,4,2) || '-' ||
                                substr(hc.styleKey,6,2) <datestest>
                    group by gt.base,gt.category,upper(gt.limitType),s.name
                            <groupbygt.bigBlind>,gtId<groupbyseats>,PlPosition
                ) stats
            inner join
                ( select /* profit from handsplayers/handsactions */
                            hprof.gtId,
                            cast(case when hprof.position = 'B' then -2
                                when hprof.position = 'S' then -1
                                when hprof.position in ('3','4') then 2
                                when hprof.position in ('6','7') then 5
                                else hprof.position
                            end as signed)                           as PlPosition,
                            sum(hprof.profit) as sum_profit,
                            avg(hprof.profit/100.0) as profitperhand,
                            case when hprof.gtId = -1 then -999
                                else variance(hprof.profit/100.0)
                            end as variance
                            ,case when hprof.gtId = -1 then -999
                                else sqrt(variance(hprof.profit/100.0))
                            end as stddev
                    from
                        (select hp.handId, <hgametypeId> as gtId, hp.position
                            , hp.totalProfit as profit
                        from HandsPlayers hp
                        inner join Hands h  ON  (h.id = hp.handId)
                        where hp.playerId in <player_test>
                        and   hp.tourneysPlayersId IS NULL
                        and   datetime(h.startTime) <datestest>
                        group by hp.handId, gtId, hp.position, hp.totalProfit
                        ) hprof
                    group by hprof.gtId, PlPosition
                    ) hprof2
                on (    hprof2.gtId = stats.gtId
                    and hprof2.PlPosition = stats.PlPosition)
            order by stats.category, stats.bigBlind, stats.limitType, stats.currency, stats.maxSeats <orderbyseats>
                    ,cast(stats.PlPosition as signed)"""

        ####################################
        # Cash Game Graph query
        ####################################
        self.query['getRingProfitAllHandsPlayerIdSite'] = """
            SELECT hp.handId, hp.totalProfit, hp.sawShowdown
            FROM HandsPlayers hp
            INNER JOIN Players pl      ON  (pl.id = hp.playerId)
            INNER JOIN Hands h         ON  (h.id  = hp.handId)
            INNER JOIN Gametypes gt    ON  (gt.id = h.gametypeId)
            WHERE pl.id in <player_test>
            AND   pl.siteId in <site_test>
            AND   h.startTime > '<startdate_test>'
            AND   h.startTime < '<enddate_test>'
            <limit_test>
            <game_test>
            AND   gt.type = 'ring'
            GROUP BY h.startTime, hp.handId, hp.sawShowdown, hp.totalProfit
            ORDER BY h.startTime"""

        self.query['getRingProfitAllHandsPlayerIdSiteInBB'] = """
            SELECT hp.handId, ( hp.totalProfit / ( gt.bigBlind  * 2.0 ) ) * 100 , hp.sawShowdown, ( hp.allInEV / ( gt.bigBlind * 2.0 ) ) * 100
            FROM HandsPlayers hp
            INNER JOIN Players pl      ON  (pl.id = hp.playerId)
            INNER JOIN Hands h         ON  (h.id  = hp.handId)
            INNER JOIN Gametypes gt    ON  (gt.id = h.gametypeId)
            WHERE pl.id in <player_test>
            AND   pl.siteId in <site_test>
            AND   h.startTime > '<startdate_test>'
            AND   h.startTime < '<enddate_test>'
            <limit_test>
            <game_test>
            <currency_test>
            AND   hp.tourneysPlayersId IS NULL
            GROUP BY h.startTime, hp.handId, hp.sawShowdown, hp.totalProfit, hp.allInEV, gt.bigBlind
            ORDER BY h.startTime"""

        self.query['getRingProfitAllHandsPlayerIdSiteInDollars'] = """
            SELECT hp.handId, hp.totalProfit, hp.sawShowdown, hp.allInEV
            FROM HandsPlayers hp
            INNER JOIN Players pl      ON  (pl.id = hp.playerId)
            INNER JOIN Hands h         ON  (h.id  = hp.handId)
            INNER JOIN Gametypes gt    ON  (gt.id = h.gametypeId)
            WHERE pl.id in <player_test>
            AND   pl.siteId in <site_test>
            AND   h.startTime > '<startdate_test>'
            AND   h.startTime < '<enddate_test>'
            <limit_test>
            <game_test>
            <currency_test>
            AND   hp.tourneysPlayersId IS NULL
            GROUP BY h.startTime, hp.handId, hp.sawShowdown, hp.totalProfit, hp.allInEV
            ORDER BY h.startTime"""

        ####################################
        # Tourney Results query
        ####################################
        self.query['tourneyResults'] = """
            SELECT tp.tourneyId, (coalesce(tp.winnings,0) - coalesce(tt.buyIn,0) - coalesce(tt.fee,0)) as profit, tp.koCount, tp.rebuyCount, tp.addOnCount, tt.buyIn, tt.fee, t.siteTourneyNo
            FROM TourneysPlayers tp
            INNER JOIN Players pl      ON  (pl.id = tp.playerId)
            INNER JOIN Tourneys t         ON  (t.id  = tp.tourneyId)
            INNER JOIN TourneyTypes tt    ON  (tt.id = t.tourneyTypeId)
            WHERE pl.id in <player_test>
            AND   pl.siteId in <site_test>
            AND   ((t.startTime > '<startdate_test>' AND t.startTime < '<enddate_test>')
                    OR t.startTime is NULL)
            GROUP BY t.startTime, tp.tourneyId, tp.winningsCurrency,
                     tp.winnings, tp.koCount,
                     tp.rebuyCount, tp.addOnCount,
                     tt.buyIn, tt.fee, t.siteTourneyNo
            ORDER BY t.startTime"""

            #AND   gt.type = 'ring'
            #<limit_test>
            #<game_test>
            
        ####################################
        # Tourney Graph query
        # FIXME this is a horrible hack to prevent nonsense data
        #  being graphed - needs proper fix mantis #180 +#182
        ####################################
        self.query['tourneyGraph'] = """
            SELECT tp.tourneyId, (coalesce(tp.winnings,0) - coalesce(tt.buyIn,0) - coalesce(tt.fee,0)) as profit, tp.koCount, tp.rebuyCount, tp.addOnCount, tt.buyIn, tt.fee, t.siteTourneyNo
            FROM TourneysPlayers tp
            INNER JOIN Players pl      ON  (pl.id = tp.playerId)
            INNER JOIN Tourneys t         ON  (t.id  = tp.tourneyId)
            INNER JOIN TourneyTypes tt    ON  (tt.id = t.tourneyTypeId)
            WHERE pl.id in <player_test>
            AND   pl.siteId in <site_test>
            AND   (t.startTime > '<startdate_test>' AND t.startTime < '<enddate_test>')
                 <currency_test>
            GROUP BY t.startTime, tp.tourneyId, tp.winningsCurrency,
                     tp.winnings, tp.koCount,
                     tp.rebuyCount, tp.addOnCount,
                     tt.buyIn, tt.fee, t.siteTourneyNo
            ORDER BY t.startTime"""

            #AND   gt.type = 'ring'
            #<limit_test>
            #<game_test>
         ####################################
        # Tourney Graph query with tourneytypefilter
        # FIXME this is a horrible hack to prevent nonsense data
        #  being graphed - needs proper fix mantis #180 +#182
        ####################################
        self.query['tourneyGraphType'] = """
            SELECT tp.tourneyId, (coalesce(tp.winnings,0) - coalesce(tt.buyIn,0) - coalesce(tt.fee,0)) as profit, tp.koCount, tp.rebuyCount, tp.addOnCount, tt.buyIn, tt.fee, t.siteTourneyNo
            FROM TourneysPlayers tp
            INNER JOIN Players pl      ON  (pl.id = tp.playerId)
            INNER JOIN Tourneys t         ON  (t.id  = tp.tourneyId)
            INNER JOIN TourneyTypes tt    ON  (tt.id = t.tourneyTypeId)
            WHERE pl.id in <player_test>
            AND   pl.siteId in <site_test>
            AND tt.category in <tourney_cat>
            AND tt.limitType in <tourney_lim>
            AND tt.buyin in <tourney_buyin>
            AND   (t.startTime > '<startdate_test>' AND t.startTime < '<enddate_test>')
                 <currency_test>
            GROUP BY t.startTime, tp.tourneyId, tp.winningsCurrency,
                     tp.winnings, tp.koCount,
                     tp.rebuyCount, tp.addOnCount,
                     tt.buyIn, tt.fee, t.siteTourneyNo
            ORDER BY t.startTime"""

            #AND   gt.type = 'ring'
            #<limit_test>
            #<game_test>           
        
        ####################################
        # Session stats query
        ####################################
        self.query['sessionStats'] = """
            SELECT STRFTIME('<ampersand_s>', h.startTime) as time, hp.totalProfit
            FROM HandsPlayers hp
                INNER JOIN Hands h       on  (h.id = hp.handId)
                INNER JOIN Gametypes gt  on  (gt.Id = h.gametypeId)
                INNER JOIN Sites s       on  (s.Id = gt.siteId)
                INNER JOIN Players p     on  (p.Id = hp.playerId)
            WHERE hp.playerId in <player_test>
                AND  h.startTime <datestest>
                AND  gt.type is 'ring'
                <limit_test>
                <game_test>
                <seats_test>
                <currency_test>
            ORDER by time"""

        ####################################
        # Querry to get all hands in a date range
        ####################################
        self.query['handsInRange'] = """
            select h.id
                from Hands h
                join HandsPlayers hp on h.id = hp.handId
                join Gametypes gt on gt.id = h.gametypeId
            where h.startTime <datetest>
                and hp.playerId in <player_test>
                <game_test>
                <limit_test>
                <position_test>"""

        ####################################
        # Querry to get all hands in a date range for cash games session
        ####################################
        self.query['handsInRangeSession'] = """
            select h.id
                from Hands h
                
            where h.startTime <datetest>
               """
        

        ####################################
        # Querry to get all hands in a date range for cash games session variation filter
        ####################################
        self.query['handsInRangeSessionFilter'] = """
            select h.id
            from Hands h
            join Gametypes gt on h.gametypeId = gt.id
            join HandsPlayers hp on h.id = hp.handId  -- utilisation de HandsPlayers
            where h.startTime <datetest>
            <game_test>
            <limit_test>
            <player_test>
            <position_test>
        """

        self.query['getPlayerId'] = """
            SELECT id 
            FROM Players 
            WHERE siteId = %s 
            AND name = %s
        """

        ####################################
        # Query to get a single hand for the replayer
        ####################################
        self.query['singleHand'] = """
                 SELECT h.*
                    FROM Hands h
                    WHERE id = %s"""

        ####################################
        # Query to get run it twice boards for the replayer
        ####################################
        self.query['singleHandBoards'] = """
                 SELECT b.*
                    FROM Boards b
                    WHERE handId = %s"""

        ####################################
        # Query to get a single player hand for the replayer
        ####################################
        self.query['playerHand'] = """
            SELECT
                        hp.seatno,
                        round(hp.winnings / 100.0,2) as winnings,
                        p.name,
                        round(hp.startCash / 100.0,2) as chips,
                        hp.card1,hp.card2,hp.card3,hp.card4,hp.card5,
                        hp.card6,hp.card7,hp.card8,hp.card9,hp.card10,
                        hp.card11,hp.card12,hp.card13,hp.card14,hp.card15,
                        hp.card16,hp.card17,hp.card18,hp.card19,hp.card20,
                        hp.position,
                        round(hp.startBounty / 100.0,2) as bounty,
                        hp.sitout
                    FROM
                        HandsPlayers as hp,
                        Players as p
                    WHERE
                        hp.handId = %s
                        and p.id = hp.playerId
                    ORDER BY
                        hp.seatno
                """

        ####################################
        # Query for the actions of a hand
        ####################################
        self.query['handActions'] = """
            SELECT
                      ha.actionNo,
                      p.name,
                      ha.street,
                      ha.actionId,
                      ha.allIn,
                      round(ha.amount / 100.0,2) as bet,
                      ha.numDiscarded,
                      ha.cardsDiscarded
                FROM
                      HandsActions as ha,
                      Players as p,
                      Hands as h
                WHERE
                          h.id = %s
                      AND ha.handId = h.id
                      AND ha.playerId = p.id
                ORDER BY
                      ha.id ASC
                """

        ####################################
        # Queries to rebuild/modify hudcache
        ####################################
      
        self.query['clearHudCache'] = """DELETE FROM HudCache"""
        self.query['clearCardsCache'] = """DELETE FROM CardsCache"""
        self.query['clearPositionsCache'] = """DELETE FROM PositionsCache"""
        
        self.query['clearHudCacheTourneyType'] = """DELETE FROM HudCache WHERE tourneyTypeId = %s"""
        self.query['clearCardsCacheTourneyType'] = """DELETE FROM CardsCache WHERE tourneyTypeId = %s"""
        self.query['clearPositionsCacheTourneyType'] = """DELETE FROM PositionsCache WHERE tourneyTypeId = %s"""  
        
        self.query['fetchNewHudCacheTourneyTypeIds'] = """SELECT TT.id
                                                    FROM TourneyTypes TT
                                                    LEFT OUTER JOIN HudCache HC ON (TT.id = HC.tourneyTypeId)
                                                    WHERE HC.tourneyTypeId is NULL"""
                
        self.query['fetchNewCardsCacheTourneyTypeIds'] = """SELECT TT.id
                                                    FROM TourneyTypes TT
                                                    LEFT OUTER JOIN CardsCache CC ON (TT.id = CC.tourneyTypeId)
                                                    WHERE CC.tourneyTypeId is NULL"""
                
        self.query['fetchNewPositionsCacheTourneyTypeIds'] = """SELECT TT.id
                                                    FROM TourneyTypes TT
                                                    LEFT OUTER JOIN PositionsCache PC ON (TT.id = PC.tourneyTypeId)
                                                    WHERE PC.tourneyTypeId is NULL"""
        
        self.query['clearCardsCacheWeeksMonths'] = """DELETE FROM CardsCache WHERE weekId = %s AND monthId = %s"""
        self.query['clearPositionsCacheWeeksMonths'] = """DELETE FROM PositionsCache WHERE weekId = %s AND monthId = %s"""  
        
        self.query['selectSessionWithWeekId'] = """SELECT id FROM Sessions WHERE weekId = %s"""
        self.query['selectSessionWithMonthId'] = """SELECT id FROM Sessions WHERE monthId = %s"""
        
        self.query['deleteWeekId'] = """DELETE FROM Weeks WHERE id = %s"""
        self.query['deleteMonthId'] = """DELETE FROM Months WHERE id = %s"""
        
        self.query['fetchNewCardsCacheWeeksMonths'] = """SELECT SCG.weekId, SCG.monthId
                                            FROM (SELECT DISTINCT weekId, monthId FROM Sessions) SCG
                                            LEFT OUTER JOIN CardsCache CC ON (SCG.weekId = CC.weekId AND SCG.monthId = CC.monthId)
                                            WHERE CC.weekId is NULL OR CC.monthId is NULL"""
        
        self.query['fetchNewPositionsCacheWeeksMonths'] = """SELECT SCG.weekId, SCG.monthId
                                            FROM (SELECT DISTINCT weekId, monthId FROM Sessions) SCG
                                            LEFT OUTER JOIN PositionsCache PC ON (SCG.weekId = PC.weekId AND SCG.monthId = PC.monthId)
                                            WHERE PC.weekId is NULL OR PC.monthId is NULL"""
        
            

        self.query['rebuildCache'] = """insert into <insert>
            ,n
            ,street0VPIChance
            ,street0VPI
            ,street0AggrChance
            ,street0Aggr
            ,street0CalledRaiseChance
            ,street0CalledRaiseDone
            ,street0_2BChance
            ,street0_2BDone
            ,street0_3BChance
            ,street0_3BDone
            ,street0_4BChance
            ,street0_4BDone
            ,street0_C4BChance
            ,street0_C4BDone
            ,street0_FoldTo2BChance
            ,street0_FoldTo2BDone
            ,street0_FoldTo3BChance
            ,street0_FoldTo3BDone
            ,street0_FoldTo4BChance
            ,street0_FoldTo4BDone
            ,street0_SqueezeChance
            ,street0_SqueezeDone
            ,raiseToStealChance
            ,raiseToStealDone
            ,stealChance
            ,stealDone
            ,success_Steal
            ,street1Seen
            ,street2Seen
            ,street3Seen
            ,street4Seen
            ,sawShowdown
            ,street1Aggr
            ,street2Aggr
            ,street3Aggr
            ,street4Aggr
            ,otherRaisedStreet0
            ,otherRaisedStreet1
            ,otherRaisedStreet2
            ,otherRaisedStreet3
            ,otherRaisedStreet4
            ,foldToOtherRaisedStreet0
            ,foldToOtherRaisedStreet1
            ,foldToOtherRaisedStreet2
            ,foldToOtherRaisedStreet3
            ,foldToOtherRaisedStreet4
            ,wonWhenSeenStreet1
            ,wonWhenSeenStreet2
            ,wonWhenSeenStreet3
            ,wonWhenSeenStreet4
            ,wonAtSD
            ,raiseFirstInChance
            ,raisedFirstIn
            ,foldBbToStealChance
            ,foldedBbToSteal
            ,foldSbToStealChance
            ,foldedSbToSteal
            ,street1CBChance
            ,street1CBDone
            ,street2CBChance
            ,street2CBDone
            ,street3CBChance
            ,street3CBDone
            ,street4CBChance
            ,street4CBDone
            ,foldToStreet1CBChance
            ,foldToStreet1CBDone
            ,foldToStreet2CBChance
            ,foldToStreet2CBDone
            ,foldToStreet3CBChance
            ,foldToStreet3CBDone
            ,foldToStreet4CBChance
            ,foldToStreet4CBDone
            ,common
            ,committed
            ,winnings
            ,rake
            ,rakeDealt
            ,rakeContributed
            ,rakeWeighted
            ,totalProfit
            ,allInEV
            ,showdownWinnings
            ,nonShowdownWinnings
            ,street1CheckCallRaiseChance
            ,street1CheckCallDone
            ,street1CheckRaiseDone
            ,street2CheckCallRaiseChance
            ,street2CheckCallDone
            ,street2CheckRaiseDone
            ,street3CheckCallRaiseChance
            ,street3CheckCallDone
            ,street3CheckRaiseDone
            ,street4CheckCallRaiseChance
            ,street4CheckCallDone
            ,street4CheckRaiseDone
            ,street0Calls
            ,street1Calls
            ,street2Calls
            ,street3Calls
            ,street4Calls
            ,street0Bets
            ,street1Bets
            ,street2Bets
            ,street3Bets
            ,street4Bets
            ,street0Raises
            ,street1Raises
            ,street2Raises
            ,street3Raises
            ,street4Raises
            ,street1Discards
            ,street2Discards
            ,street3Discards
            )
            SELECT <select>
                    ,count(1)
                    ,sum(CAST(street0VPIChance as integer))
                    ,sum(CAST(street0VPI as integer))
                    ,sum(CAST(street0AggrChance as integer))
                    ,sum(CAST(street0Aggr as integer))
                    ,sum(CAST(street0CalledRaiseChance as integer))
                    ,sum(CAST(street0CalledRaiseDone as integer))
                    ,sum(CAST(street0_2BChance as integer))
                    ,sum(CAST(street0_2BDone as integer))
                    ,sum(CAST(street0_3BChance as integer))
                    ,sum(CAST(street0_3BDone as integer))
                    ,sum(CAST(street0_4BChance as integer))
                    ,sum(CAST(street0_4BDone as integer))
                    ,sum(CAST(street0_C4BChance as integer))
                    ,sum(CAST(street0_C4BDone as integer))
                    ,sum(CAST(street0_FoldTo2BChance as integer))
                    ,sum(CAST(street0_FoldTo2BDone as integer))
                    ,sum(CAST(street0_FoldTo3BChance as integer))
                    ,sum(CAST(street0_FoldTo3BDone as integer))
                    ,sum(CAST(street0_FoldTo4BChance as integer))
                    ,sum(CAST(street0_FoldTo4BDone as integer))
                    ,sum(CAST(street0_SqueezeChance as integer))
                    ,sum(CAST(street0_SqueezeDone as integer))
                    ,sum(CAST(raiseToStealChance as integer))
                    ,sum(CAST(raiseToStealDone as integer))
                    ,sum(CAST(stealChance as integer))
                    ,sum(CAST(stealDone as integer))
                    ,sum(CAST(success_Steal as integer))
                    ,sum(CAST(street1Seen as integer))
                    ,sum(CAST(street2Seen as integer))
                    ,sum(CAST(street3Seen as integer))
                    ,sum(CAST(street4Seen as integer))
                    ,sum(CAST(sawShowdown as integer))
                    ,sum(CAST(street1Aggr as integer))
                    ,sum(CAST(street2Aggr as integer))
                    ,sum(CAST(street3Aggr as integer))
                    ,sum(CAST(street4Aggr as integer))
                    ,sum(CAST(otherRaisedStreet0 as integer))
                    ,sum(CAST(otherRaisedStreet1 as integer))
                    ,sum(CAST(otherRaisedStreet2 as integer))
                    ,sum(CAST(otherRaisedStreet3 as integer))
                    ,sum(CAST(otherRaisedStreet4 as integer))
                    ,sum(CAST(foldToOtherRaisedStreet0 as integer))
                    ,sum(CAST(foldToOtherRaisedStreet1 as integer))
                    ,sum(CAST(foldToOtherRaisedStreet2 as integer))
                    ,sum(CAST(foldToOtherRaisedStreet3 as integer))
                    ,sum(CAST(foldToOtherRaisedStreet4 as integer))
                    ,sum(CAST(wonWhenSeenStreet1 as integer))
                    ,sum(CAST(wonWhenSeenStreet2 as integer))
                    ,sum(CAST(wonWhenSeenStreet3 as integer))
                    ,sum(CAST(wonWhenSeenStreet4 as integer))
                    ,sum(CAST(wonAtSD as integer))
                    ,sum(CAST(raiseFirstInChance as integer))
                    ,sum(CAST(raisedFirstIn as integer))
                    ,sum(CAST(foldBbToStealChance as integer))
                    ,sum(CAST(foldedBbToSteal as integer))
                    ,sum(CAST(foldSbToStealChance as integer))
                    ,sum(CAST(foldedSbToSteal as integer))
                    ,sum(CAST(street1CBChance as integer))
                    ,sum(CAST(street1CBDone as integer))
                    ,sum(CAST(street2CBChance as integer))
                    ,sum(CAST(street2CBDone as integer))
                    ,sum(CAST(street3CBChance as integer))
                    ,sum(CAST(street3CBDone as integer))
                    ,sum(CAST(street4CBChance as integer))
                    ,sum(CAST(street4CBDone as integer))
                    ,sum(CAST(foldToStreet1CBChance as integer))
                    ,sum(CAST(foldToStreet1CBDone as integer))
                    ,sum(CAST(foldToStreet2CBChance as integer))
                    ,sum(CAST(foldToStreet2CBDone as integer))
                    ,sum(CAST(foldToStreet3CBChance as integer))
                    ,sum(CAST(foldToStreet3CBDone as integer))
                    ,sum(CAST(foldToStreet4CBChance as integer))
                    ,sum(CAST(foldToStreet4CBDone as integer))
                    ,sum(CAST(common as integer))
                    ,sum(CAST(committed as integer))
                    ,sum(CAST(winnings as integer))
                    ,sum(CAST(rake as integer))
                    ,sum(CAST(rakeDealt as integer))
                    ,sum(CAST(rakeContributed as integer))
                    ,sum(CAST(rakeWeighted as integer))
                    ,sum(CAST(totalProfit as integer))
                    ,sum(allInEV)
                    ,sum(CAST(case when sawShowdown = 1 then totalProfit else 0 end as integer))
                    ,sum(CAST(case when sawShowdown = 0 then totalProfit else 0 end as integer))
                    ,sum(CAST(street1CheckCallRaiseChance as integer))
                    ,sum(CAST(street1CheckCallDone as integer))
                    ,sum(CAST(street1CheckRaiseDone as integer))
                    ,sum(CAST(street2CheckCallRaiseChance as integer))
                    ,sum(CAST(street2CheckCallDone as integer))
                    ,sum(CAST(street2CheckRaiseDone as integer))
                    ,sum(CAST(street3CheckCallRaiseChance as integer))
                    ,sum(CAST(street3CheckCallDone as integer))
                    ,sum(CAST(street3CheckRaiseDone as integer))
                    ,sum(CAST(street4CheckCallRaiseChance as integer))
                    ,sum(CAST(street4CheckCallDone as integer))
                    ,sum(CAST(street4CheckRaiseDone as integer))
                    ,sum(CAST(street0Calls as integer))
                    ,sum(CAST(street1Calls as integer))
                    ,sum(CAST(street2Calls as integer))
                    ,sum(CAST(street3Calls as integer))
                    ,sum(CAST(street4Calls as integer))
                    ,sum(CAST(street0Bets as integer))
                    ,sum(CAST(street1Bets as integer))
                    ,sum(CAST(street2Bets as integer))
                    ,sum(CAST(street3Bets as integer))
                    ,sum(CAST(street4Bets as integer))
                    ,sum(CAST(hp.street0Raises as integer))
                    ,sum(CAST(hp.street1Raises as integer))
                    ,sum(CAST(hp.street2Raises as integer))
                    ,sum(CAST(hp.street3Raises as integer))
                    ,sum(CAST(hp.street4Raises as integer))
                    ,sum(CAST(street1Discards as integer))
                    ,sum(CAST(street2Discards as integer))
                    ,sum(CAST(street3Discards as integer))
            FROM Hands h
            INNER JOIN HandsPlayers hp ON (h.id = hp.handId<hero_join>)
            INNER JOIN Gametypes g ON (h.gametypeId = g.id)
            <sessions_join_clause>
            <tourney_join_clause>
            <where_clause>
            GROUP BY <group>"""


        self.query['insert_hudcache'] = """insert into HudCache (
                gametypeId,
                playerId,
                seats,
                position,
                tourneyTypeId,
                styleKey,
                n,
                street0VPIChance,
                street0VPI,
                street0AggrChance,
                street0Aggr,
                street0CalledRaiseChance,
                street0CalledRaiseDone,
                street0_2BChance,
                street0_2BDone,
                street0_3BChance,
                street0_3BDone,
                street0_4BChance,
                street0_4BDone,
                street0_C4BChance,
                street0_C4BDone,
                street0_FoldTo2BChance,
                street0_FoldTo2BDone,
                street0_FoldTo3BChance,
                street0_FoldTo3BDone,
                street0_FoldTo4BChance,
                street0_FoldTo4BDone,
                street0_SqueezeChance,
                street0_SqueezeDone,
                raiseToStealChance,
                raiseToStealDone,
                stealChance,
                stealDone,
                success_Steal,
                street1Seen,
                street2Seen,
                street3Seen,
                street4Seen,
                sawShowdown,
                street1Aggr,
                street2Aggr,
                street3Aggr,
                street4Aggr,
                otherRaisedStreet0,
                otherRaisedStreet1,
                otherRaisedStreet2,
                otherRaisedStreet3,
                otherRaisedStreet4,
                foldToOtherRaisedStreet0,
                foldToOtherRaisedStreet1,
                foldToOtherRaisedStreet2,
                foldToOtherRaisedStreet3,
                foldToOtherRaisedStreet4,
                wonWhenSeenStreet1,
                wonWhenSeenStreet2,
                wonWhenSeenStreet3,
                wonWhenSeenStreet4,
                wonAtSD,
                raiseFirstInChance,
                raisedFirstIn,
                foldBbToStealChance,
                foldedBbToSteal,
                foldSbToStealChance,
                foldedSbToSteal,
                street1CBChance,
                street1CBDone,
                street2CBChance,
                street2CBDone,
                street3CBChance,
                street3CBDone,
                street4CBChance,
                street4CBDone,
                foldToStreet1CBChance,
                foldToStreet1CBDone,
                foldToStreet2CBChance,
                foldToStreet2CBDone,
                foldToStreet3CBChance,
                foldToStreet3CBDone,
                foldToStreet4CBChance,
                foldToStreet4CBDone,
                common,
                committed,
                winnings,
                rake,
                rakeDealt,
                rakeContributed,
                rakeWeighted,
                totalProfit,
                allInEV,
                showdownWinnings,
                nonShowdownWinnings,
                street1CheckCallRaiseChance,
                street1CheckCallDone,
                street1CheckRaiseDone,
                street2CheckCallRaiseChance,
                street2CheckCallDone,
                street2CheckRaiseDone,
                street3CheckCallRaiseChance,
                street3CheckCallDone,
                street3CheckRaiseDone,
                street4CheckCallRaiseChance,
                street4CheckCallDone,
                street4CheckRaiseDone,
                street0Calls,
                street1Calls,
                street2Calls,
                street3Calls,
                street4Calls,
                street0Bets,
                street1Bets,
                street2Bets,
                street3Bets,
                street4Bets,
                street0Raises,
                street1Raises,
                street2Raises,
                street3Raises,
                street4Raises,
                street1Discards,
                street2Discards,
                street3Discards)
            values (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s)"""

        self.query['update_hudcache'] = """
            UPDATE HudCache SET
            n=n+%s,
            street0VPIChance=street0VPIChance+%s,
            street0VPI=street0VPI+%s,
            street0AggrChance=street0AggrChance+%s,
            street0Aggr=street0Aggr+%s,
            street0CalledRaiseChance=street0CalledRaiseChance+%s,
            street0CalledRaiseDone=street0CalledRaiseDone+%s,
            street0_2BChance=street0_2BChance+%s,
            street0_2BDone=street0_2BDone+%s,
            street0_3BChance=street0_3BChance+%s,
            street0_3BDone=street0_3BDone+%s,
            street0_4BChance=street0_4BChance+%s,
            street0_4BDone=street0_4BDone+%s,
            street0_C4BChance=street0_C4BChance+%s,
            street0_C4BDone=street0_C4BDone+%s,
            street0_FoldTo2BChance=street0_FoldTo2BChance+%s,
            street0_FoldTo2BDone=street0_FoldTo2BDone+%s,
            street0_FoldTo3BChance=street0_FoldTo3BChance+%s,
            street0_FoldTo3BDone=street0_FoldTo3BDone+%s,
            street0_FoldTo4BChance=street0_FoldTo4BChance+%s,
            street0_FoldTo4BDone=street0_FoldTo4BDone+%s,
            street0_SqueezeChance=street0_SqueezeChance+%s,
            street0_SqueezeDone=street0_SqueezeDone+%s,
            raiseToStealChance=raiseToStealChance+%s,
            raiseToStealDone=raiseToStealDone+%s,
            stealChance=stealChance+%s,
            stealDone=stealDone+%s,
            success_Steal=success_Steal+%s,
            street1Seen=street1Seen+%s,
            street2Seen=street2Seen+%s,
            street3Seen=street3Seen+%s,
            street4Seen=street4Seen+%s,
            sawShowdown=sawShowdown+%s,
            street1Aggr=street1Aggr+%s,
            street2Aggr=street2Aggr+%s,
            street3Aggr=street3Aggr+%s,
            street4Aggr=street4Aggr+%s,
            otherRaisedStreet0=otherRaisedStreet0+%s,
            otherRaisedStreet1=otherRaisedStreet1+%s,
            otherRaisedStreet2=otherRaisedStreet2+%s,
            otherRaisedStreet3=otherRaisedStreet3+%s,
            otherRaisedStreet4=otherRaisedStreet4+%s,
            foldToOtherRaisedStreet0=foldToOtherRaisedStreet0+%s,
            foldToOtherRaisedStreet1=foldToOtherRaisedStreet1+%s,
            foldToOtherRaisedStreet2=foldToOtherRaisedStreet2+%s,
            foldToOtherRaisedStreet3=foldToOtherRaisedStreet3+%s,
            foldToOtherRaisedStreet4=foldToOtherRaisedStreet4+%s,
            wonWhenSeenStreet1=wonWhenSeenStreet1+%s,
            wonWhenSeenStreet2=wonWhenSeenStreet2+%s,
            wonWhenSeenStreet3=wonWhenSeenStreet3+%s,
            wonWhenSeenStreet4=wonWhenSeenStreet4+%s,
            wonAtSD=wonAtSD+%s,
            raiseFirstInChance=raiseFirstInChance+%s,
            raisedFirstIn=raisedFirstIn+%s,
            foldBbToStealChance=foldBbToStealChance+%s,
            foldedBbToSteal=foldedBbToSteal+%s,
            foldSbToStealChance=foldSbToStealChance+%s,
            foldedSbToSteal=foldedSbToSteal+%s,
            street1CBChance=street1CBChance+%s,
            street1CBDone=street1CBDone+%s,
            street2CBChance=street2CBChance+%s,
            street2CBDone=street2CBDone+%s,
            street3CBChance=street3CBChance+%s,
            street3CBDone=street3CBDone+%s,
            street4CBChance=street4CBChance+%s,
            street4CBDone=street4CBDone+%s,
            foldToStreet1CBChance=foldToStreet1CBChance+%s,
            foldToStreet1CBDone=foldToStreet1CBDone+%s,
            foldToStreet2CBChance=foldToStreet2CBChance+%s,
            foldToStreet2CBDone=foldToStreet2CBDone+%s,
            foldToStreet3CBChance=foldToStreet3CBChance+%s,
            foldToStreet3CBDone=foldToStreet3CBDone+%s,
            foldToStreet4CBChance=foldToStreet4CBChance+%s,
            foldToStreet4CBDone=foldToStreet4CBDone+%s,
            common=common+%s,
            committed=committed+%s,
            winnings=winnings+%s,
            rake=rake+%s,
            rakeDealt=rakeDealt+%s,
            rakeContributed=rakeContributed+%s,
            rakeWeighted=rakeWeighted+%s,
            totalProfit=totalProfit+%s,
            allInEV=allInEV+%s,
            showdownWinnings=showdownWinnings+%s,
            nonShowdownWinnings=nonShowdownWinnings+%s,
            street1CheckCallRaiseChance=street1CheckCallRaiseChance+%s,
            street1CheckCallDone=street1CheckCallDone+%s,
            street1CheckRaiseDone=street1CheckRaiseDone+%s,
            street2CheckCallRaiseChance=street2CheckCallRaiseChance+%s,
            street2CheckCallDone=street2CheckCallDone+%s,
            street2CheckRaiseDone=street2CheckRaiseDone+%s,
            street3CheckCallRaiseChance=street3CheckCallRaiseChance+%s,
            street3CheckCallDone=street3CheckCallDone+%s,
            street3CheckRaiseDone=street3CheckRaiseDone+%s,
            street4CheckCallRaiseChance=street4CheckCallRaiseChance+%s,
            street4CheckCallDone=street4CheckCallDone+%s,
            street4CheckRaiseDone=street4CheckRaiseDone+%s,
            street0Calls=street0Calls+%s,
            street1Calls=street1Calls+%s,
            street2Calls=street2Calls+%s,
            street3Calls=street3Calls+%s,
            street4Calls=street4Calls+%s,
            street0Bets=street0Bets+%s, 
            street1Bets=street1Bets+%s,
            street2Bets=street2Bets+%s, 
            street3Bets=street3Bets+%s,
            street4Bets=street4Bets+%s, 
            street0Raises=street0Raises+%s,
            street1Raises=street1Raises+%s,
            street2Raises=street2Raises+%s,
            street3Raises=street3Raises+%s,
            street4Raises=street4Raises+%s,            
            street1Discards=street1Discards+%s,
            street2Discards=street2Discards+%s,
            street3Discards=street3Discards+%s
        WHERE id=%s"""
            
        self.query['select_hudcache_ring'] = """
                    SELECT id
                    FROM HudCache
                    WHERE gametypeId=%s
                    AND   playerId=%s
                    AND   seats=%s
                    AND   position=%s
                    AND   tourneyTypeId is NULL
                    AND   styleKey = %s"""
                    
        self.query['select_hudcache_tour'] = """
                    SELECT id
                    FROM HudCache
                    WHERE gametypeId=%s
                    AND   playerId=%s
                    AND   seats=%s
                    AND   position=%s
                    AND   tourneyTypeId=%s
                    AND   styleKey = %s"""
            
        self.query['get_hero_hudcache_start'] = """select min(hc.styleKey)
                                                   from HudCache hc
                                                   where hc.playerId in <playerid_list>
                                                   and   hc.styleKey like 'd%'"""
                                                   
        ####################################
        # Queries to insert/update cardscache
        ####################################
                                                   
        self.query['insert_cardscache'] = """insert into CardsCache (
                weekId,
                monthId,
                gametypeId,
                tourneyTypeId,
                playerId,
                startCards,
                n,
                street0VPIChance,
                street0VPI,
                street0AggrChance,
                street0Aggr,
                street0CalledRaiseChance,
                street0CalledRaiseDone,
                street0_3BChance,
                street0_3BDone,
                street0_2BChance,
                street0_2BDone,
                street0_4BChance,
                street0_4BDone,
                street0_C4BChance,
                street0_C4BDone,
                street0_FoldTo2BChance,
                street0_FoldTo2BDone,
                street0_FoldTo3BChance,
                street0_FoldTo3BDone,
                street0_FoldTo4BChance,
                street0_FoldTo4BDone,
                street0_SqueezeChance,
                street0_SqueezeDone,
                raiseToStealChance,
                raiseToStealDone,
                stealChance,
                stealDone,
                success_Steal,
                street1Seen,
                street2Seen,
                street3Seen,
                street4Seen,
                sawShowdown,
                street1Aggr,
                street2Aggr,
                street3Aggr,
                street4Aggr,
                otherRaisedStreet0,
                otherRaisedStreet1,
                otherRaisedStreet2,
                otherRaisedStreet3,
                otherRaisedStreet4,
                foldToOtherRaisedStreet0,
                foldToOtherRaisedStreet1,
                foldToOtherRaisedStreet2,
                foldToOtherRaisedStreet3,
                foldToOtherRaisedStreet4,
                wonWhenSeenStreet1,
                wonWhenSeenStreet2,
                wonWhenSeenStreet3,
                wonWhenSeenStreet4,
                wonAtSD,
                raiseFirstInChance,
                raisedFirstIn,
                foldBbToStealChance,
                foldedBbToSteal,
                foldSbToStealChance,
                foldedSbToSteal,
                street1CBChance,
                street1CBDone,
                street2CBChance,
                street2CBDone,
                street3CBChance,
                street3CBDone,
                street4CBChance,
                street4CBDone,
                foldToStreet1CBChance,
                foldToStreet1CBDone,
                foldToStreet2CBChance,
                foldToStreet2CBDone,
                foldToStreet3CBChance,
                foldToStreet3CBDone,
                foldToStreet4CBChance,
                foldToStreet4CBDone,
                common,
                committed,
                winnings,
                rake,
                rakeDealt,
                rakeContributed,
                rakeWeighted,
                totalProfit,
                allInEV,
                showdownWinnings,
                nonShowdownWinnings,
                street1CheckCallRaiseChance,
                street1CheckCallDone,
                street1CheckRaiseDone,
                street2CheckCallRaiseChance,
                street2CheckCallDone,
                street2CheckRaiseDone,
                street3CheckCallRaiseChance,
                street3CheckCallDone,
                street3CheckRaiseDone,
                street4CheckCallRaiseChance,
                street4CheckCallDone,
                street4CheckRaiseDone,
                street0Calls,
                street1Calls,
                street2Calls,
                street3Calls,
                street4Calls,
                street0Bets,
                street1Bets,
                street2Bets,
                street3Bets,
                street4Bets,
                street0Raises,
                street1Raises,
                street2Raises,
                street3Raises,
                street4Raises,
                street1Discards,
                street2Discards,
                street3Discards)
            values (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s)"""

        self.query['update_cardscache'] = """
            UPDATE CardsCache SET
                    n=n+%s,
                    street0VPIChance=street0VPIChance+%s,
                    street0VPI=street0VPI+%s,
                    street0AggrChance=street0AggrChance+%s,
                    street0Aggr=street0Aggr+%s,
                    street0CalledRaiseChance=street0CalledRaiseChance+%s,
                    street0CalledRaiseDone=street0CalledRaiseDone+%s,
                    street0_2BChance=street0_2BChance+%s,
                    street0_2BDone=street0_2BDone+%s,
                    street0_3BChance=street0_3BChance+%s,
                    street0_3BDone=street0_3BDone+%s,
                    street0_4BChance=street0_4BChance+%s,
                    street0_4BDone=street0_4BDone+%s,
                    street0_C4BChance=street0_C4BChance+%s,
                    street0_C4BDone=street0_C4BDone+%s,
                    street0_FoldTo2BChance=street0_FoldTo2BChance+%s,
                    street0_FoldTo2BDone=street0_FoldTo2BDone+%s,
                    street0_FoldTo3BChance=street0_FoldTo3BChance+%s,
                    street0_FoldTo3BDone=street0_FoldTo3BDone+%s,
                    street0_FoldTo4BChance=street0_FoldTo4BChance+%s,
                    street0_FoldTo4BDone=street0_FoldTo4BDone+%s,
                    street0_SqueezeChance=street0_SqueezeChance+%s,
                    street0_SqueezeDone=street0_SqueezeDone+%s,
                    raiseToStealChance=raiseToStealChance+%s,
                    raiseToStealDone=raiseToStealDone+%s,
                    stealChance=stealChance+%s,
                    stealDone=stealDone+%s,
                    success_Steal=success_Steal+%s,
                    street1Seen=street1Seen+%s,
                    street2Seen=street2Seen+%s,
                    street3Seen=street3Seen+%s,
                    street4Seen=street4Seen+%s,
                    sawShowdown=sawShowdown+%s,
                    street1Aggr=street1Aggr+%s,
                    street2Aggr=street2Aggr+%s,
                    street3Aggr=street3Aggr+%s,
                    street4Aggr=street4Aggr+%s,
                    otherRaisedStreet0=otherRaisedStreet0+%s,
                    otherRaisedStreet1=otherRaisedStreet1+%s,
                    otherRaisedStreet2=otherRaisedStreet2+%s,
                    otherRaisedStreet3=otherRaisedStreet3+%s,
                    otherRaisedStreet4=otherRaisedStreet4+%s,
                    foldToOtherRaisedStreet0=foldToOtherRaisedStreet0+%s,
                    foldToOtherRaisedStreet1=foldToOtherRaisedStreet1+%s,
                    foldToOtherRaisedStreet2=foldToOtherRaisedStreet2+%s,
                    foldToOtherRaisedStreet3=foldToOtherRaisedStreet3+%s,
                    foldToOtherRaisedStreet4=foldToOtherRaisedStreet4+%s,
                    wonWhenSeenStreet1=wonWhenSeenStreet1+%s,
                    wonWhenSeenStreet2=wonWhenSeenStreet2+%s,
                    wonWhenSeenStreet3=wonWhenSeenStreet3+%s,
                    wonWhenSeenStreet4=wonWhenSeenStreet4+%s,
                    wonAtSD=wonAtSD+%s,
                    raiseFirstInChance=raiseFirstInChance+%s,
                    raisedFirstIn=raisedFirstIn+%s,
                    foldBbToStealChance=foldBbToStealChance+%s,
                    foldedBbToSteal=foldedBbToSteal+%s,
                    foldSbToStealChance=foldSbToStealChance+%s,
                    foldedSbToSteal=foldedSbToSteal+%s,
                    street1CBChance=street1CBChance+%s,
                    street1CBDone=street1CBDone+%s,
                    street2CBChance=street2CBChance+%s,
                    street2CBDone=street2CBDone+%s,
                    street3CBChance=street3CBChance+%s,
                    street3CBDone=street3CBDone+%s,
                    street4CBChance=street4CBChance+%s,
                    street4CBDone=street4CBDone+%s,
                    foldToStreet1CBChance=foldToStreet1CBChance+%s,
                    foldToStreet1CBDone=foldToStreet1CBDone+%s,
                    foldToStreet2CBChance=foldToStreet2CBChance+%s,
                    foldToStreet2CBDone=foldToStreet2CBDone+%s,
                    foldToStreet3CBChance=foldToStreet3CBChance+%s,
                    foldToStreet3CBDone=foldToStreet3CBDone+%s,
                    foldToStreet4CBChance=foldToStreet4CBChance+%s,
                    foldToStreet4CBDone=foldToStreet4CBDone+%s,
                    common=common+%s,
                    committed=committed+%s,
                    winnings=winnings+%s,
                    rake=rake+%s,
                    rakeDealt=rakeDealt+%s,
                    rakeContributed=rakeContributed+%s,
                    rakeWeighted=rakeWeighted+%s,
                    totalProfit=totalProfit+%s,
                    allInEV=allInEV+%s,
                    showdownWinnings=showdownWinnings+%s,
                    nonShowdownWinnings=nonShowdownWinnings+%s,
                    street1CheckCallRaiseChance=street1CheckCallRaiseChance+%s,
                    street1CheckCallDone=street1CheckCallDone+%s,
                    street1CheckRaiseDone=street1CheckRaiseDone+%s,
                    street2CheckCallRaiseChance=street2CheckCallRaiseChance+%s,
                    street2CheckCallDone=street2CheckCallDone+%s,
                    street2CheckRaiseDone=street2CheckRaiseDone+%s,
                    street3CheckCallRaiseChance=street3CheckCallRaiseChance+%s,
                    street3CheckCallDone=street3CheckCallDone+%s,
                    street3CheckRaiseDone=street3CheckRaiseDone+%s,
                    street4CheckCallRaiseChance=street4CheckCallRaiseChance+%s,
                    street4CheckCallDone=street4CheckCallDone+%s,
                    street4CheckRaiseDone=street4CheckRaiseDone+%s,
                    street0Calls=street0Calls+%s,
                    street1Calls=street1Calls+%s,
                    street2Calls=street2Calls+%s,
                    street3Calls=street3Calls+%s,
                    street4Calls=street4Calls+%s,
                    street0Bets=street0Bets+%s, 
                    street1Bets=street1Bets+%s,
                    street2Bets=street2Bets+%s, 
                    street3Bets=street3Bets+%s,
                    street4Bets=street4Bets+%s, 
                    street0Raises=street0Raises+%s,
                    street1Raises=street1Raises+%s,
                    street2Raises=street2Raises+%s,
                    street3Raises=street3Raises+%s,
                    street4Raises=street4Raises+%s,
                    street1Discards=street1Discards+%s,
                    street2Discards=street2Discards+%s,
                    street3Discards=street3Discards+%s
        WHERE     id=%s"""
            
        self.query['select_cardscache_ring'] = """
                    SELECT id
                    FROM CardsCache
                    WHERE weekId=%s
                    AND   monthId=%s
                    AND   gametypeId=%s
                    AND   tourneyTypeId is NULL
                    AND   playerId=%s
                    AND   startCards=%s"""
                    
        self.query['select_cardscache_tour'] = """
                    SELECT id
                    FROM CardsCache
                    WHERE weekId=%s
                    AND   monthId=%s
                    AND   gametypeId=%s
                    AND   tourneyTypeId=%s
                    AND   playerId=%s
                    AND   startCards=%s"""
                   

        ####################################
        # create comment on players
        ####################################

        self.query['get_player_comment'] = """
            SELECT comment FROM Players WHERE id=%s
        """

        self.query['update_player_comment'] = """
            UPDATE Players SET comment=%s, commentTs=CURRENT_TIMESTAMP WHERE id=%s
        """
        self.query['get_player_name'] = "SELECT name FROM Players WHERE id=%s"

        ####################################

        ####################################
        # Queries to insert/update positionscache
        ####################################
                   
        self.query['insert_positionscache'] = """insert into PositionsCache (
                weekId,
                monthId,
                gametypeId,
                tourneyTypeId,
                playerId,
                seats,
                maxPosition,
                position,
                n,
                street0VPIChance,
                street0VPI,
                street0AggrChance,
                street0Aggr,
                street0CalledRaiseChance,
                street0CalledRaiseDone,
                street0_2BChance,
                street0_2BDone,
                street0_3BChance,
                street0_3BDone,
                street0_4BChance,
                street0_4BDone,
                street0_C4BChance,
                street0_C4BDone,
                street0_FoldTo2BChance,
                street0_FoldTo2BDone,
                street0_FoldTo3BChance,
                street0_FoldTo3BDone,
                street0_FoldTo4BChance,
                street0_FoldTo4BDone,
                street0_SqueezeChance,
                street0_SqueezeDone,
                raiseToStealChance,
                raiseToStealDone,
                stealChance,
                stealDone,
                success_Steal,
                street1Seen,
                street2Seen,
                street3Seen,
                street4Seen,
                sawShowdown,
                street1Aggr,
                street2Aggr,
                street3Aggr,
                street4Aggr,
                otherRaisedStreet0,
                otherRaisedStreet1,
                otherRaisedStreet2,
                otherRaisedStreet3,
                otherRaisedStreet4,
                foldToOtherRaisedStreet0,
                foldToOtherRaisedStreet1,
                foldToOtherRaisedStreet2,
                foldToOtherRaisedStreet3,
                foldToOtherRaisedStreet4,
                wonWhenSeenStreet1,
                wonWhenSeenStreet2,
                wonWhenSeenStreet3,
                wonWhenSeenStreet4,
                wonAtSD,
                raiseFirstInChance,
                raisedFirstIn,
                foldBbToStealChance,
                foldedBbToSteal,
                foldSbToStealChance,
                foldedSbToSteal,
                street1CBChance,
                street1CBDone,
                street2CBChance,
                street2CBDone,
                street3CBChance,
                street3CBDone,
                street4CBChance,
                street4CBDone,
                foldToStreet1CBChance,
                foldToStreet1CBDone,
                foldToStreet2CBChance,
                foldToStreet2CBDone,
                foldToStreet3CBChance,
                foldToStreet3CBDone,
                foldToStreet4CBChance,
                foldToStreet4CBDone,
                common,
                committed,
                winnings,
                rake,
                rakeDealt,
                rakeContributed,
                rakeWeighted,
                totalProfit,
                allInEV,
                showdownWinnings,
                nonShowdownWinnings,
                street1CheckCallRaiseChance,
                street1CheckCallDone,
                street1CheckRaiseDone,
                street2CheckCallRaiseChance,
                street2CheckCallDone,
                street2CheckRaiseDone,
                street3CheckCallRaiseChance,
                street3CheckCallDone,
                street3CheckRaiseDone,
                street4CheckCallRaiseChance,
                street4CheckCallDone,
                street4CheckRaiseDone,
                street0Calls,
                street1Calls,
                street2Calls,
                street3Calls,
                street4Calls,
                street0Bets,
                street1Bets,
                street2Bets,
                street3Bets,
                street4Bets,
                street0Raises,
                street1Raises,
                street2Raises,
                street3Raises,
                street4Raises,
                street1Discards,
                street2Discards,
                street3Discards)
            values (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s
                    )"""

        self.query['update_positionscache'] = """
            UPDATE PositionsCache SET
                    n=n+%s,
                    street0VPIChance=street0VPIChance+%s,
                    street0VPI=street0VPI+%s,
                    street0AggrChance=street0AggrChance+%s,
                    street0Aggr=street0Aggr+%s,
                    street0CalledRaiseChance=street0CalledRaiseChance+%s,
                    street0CalledRaiseDone=street0CalledRaiseDone+%s,
                    street0_2BChance=street0_2BChance+%s,
                    street0_2BDone=street0_2BDone+%s,
                    street0_3BChance=street0_3BChance+%s,
                    street0_3BDone=street0_3BDone+%s,
                    street0_4BChance=street0_4BChance+%s,
                    street0_4BDone=street0_4BDone+%s,
                    street0_C4BChance=street0_C4BChance+%s,
                    street0_C4BDone=street0_C4BDone+%s,
                    street0_FoldTo2BChance=street0_FoldTo2BChance+%s,
                    street0_FoldTo2BDone=street0_FoldTo2BDone+%s,
                    street0_FoldTo3BChance=street0_FoldTo3BChance+%s,
                    street0_FoldTo3BDone=street0_FoldTo3BDone+%s,
                    street0_FoldTo4BChance=street0_FoldTo4BChance+%s,
                    street0_FoldTo4BDone=street0_FoldTo4BDone+%s,
                    street0_SqueezeChance=street0_SqueezeChance+%s,
                    street0_SqueezeDone=street0_SqueezeDone+%s,
                    raiseToStealChance=raiseToStealChance+%s,
                    raiseToStealDone=raiseToStealDone+%s,
                    stealChance=stealChance+%s,
                    stealDone=stealDone+%s,
                    success_Steal=success_Steal+%s,
                    street1Seen=street1Seen+%s,
                    street2Seen=street2Seen+%s,
                    street3Seen=street3Seen+%s,
                    street4Seen=street4Seen+%s,
                    sawShowdown=sawShowdown+%s,
                    street1Aggr=street1Aggr+%s,
                    street2Aggr=street2Aggr+%s,
                    street3Aggr=street3Aggr+%s,
                    street4Aggr=street4Aggr+%s,
                    otherRaisedStreet0=otherRaisedStreet0+%s,
                    otherRaisedStreet1=otherRaisedStreet1+%s,
                    otherRaisedStreet2=otherRaisedStreet2+%s,
                    otherRaisedStreet3=otherRaisedStreet3+%s,
                    otherRaisedStreet4=otherRaisedStreet4+%s,
                    foldToOtherRaisedStreet0=foldToOtherRaisedStreet0+%s,
                    foldToOtherRaisedStreet1=foldToOtherRaisedStreet1+%s,
                    foldToOtherRaisedStreet2=foldToOtherRaisedStreet2+%s,
                    foldToOtherRaisedStreet3=foldToOtherRaisedStreet3+%s,
                    foldToOtherRaisedStreet4=foldToOtherRaisedStreet4+%s,
                    wonWhenSeenStreet1=wonWhenSeenStreet1+%s,
                    wonWhenSeenStreet2=wonWhenSeenStreet2+%s,
                    wonWhenSeenStreet3=wonWhenSeenStreet3+%s,
                    wonWhenSeenStreet4=wonWhenSeenStreet4+%s,
                    wonAtSD=wonAtSD+%s,
                    raiseFirstInChance=raiseFirstInChance+%s,
                    raisedFirstIn=raisedFirstIn+%s,
                    foldBbToStealChance=foldBbToStealChance+%s,
                    foldedBbToSteal=foldedBbToSteal+%s,
                    foldSbToStealChance=foldSbToStealChance+%s,
                    foldedSbToSteal=foldedSbToSteal+%s,
                    street1CBChance=street1CBChance+%s,
                    street1CBDone=street1CBDone+%s,
                    street2CBChance=street2CBChance+%s,
                    street2CBDone=street2CBDone+%s,
                    street3CBChance=street3CBChance+%s,
                    street3CBDone=street3CBDone+%s,
                    street4CBChance=street4CBChance+%s,
                    street4CBDone=street4CBDone+%s,
                    foldToStreet1CBChance=foldToStreet1CBChance+%s,
                    foldToStreet1CBDone=foldToStreet1CBDone+%s,
                    foldToStreet2CBChance=foldToStreet2CBChance+%s,
                    foldToStreet2CBDone=foldToStreet2CBDone+%s,
                    foldToStreet3CBChance=foldToStreet3CBChance+%s,
                    foldToStreet3CBDone=foldToStreet3CBDone+%s,
                    foldToStreet4CBChance=foldToStreet4CBChance+%s,
                    foldToStreet4CBDone=foldToStreet4CBDone+%s,
                    common=common+%s,
                    committed=committed+%s,
                    winnings=winnings+%s,
                    rake=rake+%s,
                    rakeDealt=rakeDealt+%s,
                    rakeContributed=rakeContributed+%s,
                    rakeWeighted=rakeWeighted+%s,
                    totalProfit=totalProfit+%s,
                    allInEV=allInEV+%s,
                    showdownWinnings=showdownWinnings+%s,
                    nonShowdownWinnings=nonShowdownWinnings+%s,
                    street1CheckCallRaiseChance=street1CheckCallRaiseChance+%s,
                    street1CheckCallDone=street1CheckCallDone+%s,
                    street1CheckRaiseDone=street1CheckRaiseDone+%s,
                    street2CheckCallRaiseChance=street2CheckCallRaiseChance+%s,
                    street2CheckCallDone=street2CheckCallDone+%s,
                    street2CheckRaiseDone=street2CheckRaiseDone+%s,
                    street3CheckCallRaiseChance=street3CheckCallRaiseChance+%s,
                    street3CheckCallDone=street3CheckCallDone+%s,
                    street3CheckRaiseDone=street3CheckRaiseDone+%s,
                    street4CheckCallRaiseChance=street4CheckCallRaiseChance+%s,
                    street4CheckCallDone=street4CheckCallDone+%s,
                    street4CheckRaiseDone=street4CheckRaiseDone+%s,
                    street0Calls=street0Calls+%s,
                    street1Calls=street1Calls+%s,
                    street2Calls=street2Calls+%s,
                    street3Calls=street3Calls+%s,
                    street4Calls=street4Calls+%s,
                    street0Bets=street0Bets+%s, 
                    street1Bets=street1Bets+%s,
                    street2Bets=street2Bets+%s, 
                    street3Bets=street3Bets+%s,
                    street4Bets=street4Bets+%s, 
                    street0Raises=street0Raises+%s,
                    street1Raises=street1Raises+%s,
                    street2Raises=street2Raises+%s,
                    street3Raises=street3Raises+%s,
                    street4Raises=street4Raises+%s,
                    street1Discards=street1Discards+%s,
                    street2Discards=street2Discards+%s,
                    street3Discards=street3Discards+%s
        WHERE id=%s"""
            
        self.query['select_positionscache_ring'] = """
                    SELECT id
                    FROM PositionsCache
                    WHERE weekId=%s
                    AND   monthId=%s
                    AND   gametypeId=%s
                    AND   tourneyTypeId is NULL
                    AND   playerId=%s
                    AND   seats=%s
                    AND   maxPosition=%s
                    AND   position=%s"""
                    
        self.query['select_positionscache_tour'] = """
                    SELECT id
                    FROM PositionsCache
                    WHERE weekId=%s
                    AND   monthId=%s
                    AND   gametypeId=%s
                    AND   tourneyTypeId=%s
                    AND   playerId=%s
                    AND   seats=%s
                    AND   maxPosition=%s
                    AND   position=%s"""
            
        ####################################
        # Queries to rebuild/modify sessionscache
        ####################################

        self.query['clear_S_H'] = "UPDATE Hands SET sessionId = NULL"
        self.query['clear_S_T'] = "UPDATE Tourneys SET sessionId = NULL"
        self.query['clear_S_SC'] = "UPDATE SessionsCache SET sessionId = NULL"
        self.query['clear_S_TC'] = "UPDATE TourneysCache SET sessionId = NULL"
        self.query['clear_W_S'] = "UPDATE Sessions SET weekId = NULL"
        self.query['clear_M_S'] = "UPDATE Sessions SET monthId = NULL"
        self.query['clearSessionsCache'] = "DELETE FROM SessionsCache WHERE 1"
        self.query['clearTourneysCache'] = "DELETE FROM TourneysCache WHERE 1"
        self.query['clearSessions'] = "DELETE FROM Sessions WHERE 1"
        self.query['clearWeeks'] = "DELETE FROM Weeks WHERE 1"
        self.query['clearMonths'] = "DELETE FROM Months WHERE 1"
        self.query['update_RSC_H'] = "UPDATE Hands SET sessionId = %s WHERE id = %s"
                    
        ####################################
        # select
        ####################################
        
        self.query['select_S_all'] = """
                    SELECT SC.id as id,
                    sessionStart,
                    weekStart,
                    monthStart,
                    weekId,
                    monthId
                    FROM Sessions SC
                    INNER JOIN Weeks WC ON (SC.weekId = WC.id)
                    INNER JOIN Months MC ON (SC.monthId = MC.id)
                    WHERE sessionEnd>=%s
                    AND sessionStart<=%s"""
        
        self.query['select_S'] = """
                    SELECT SC.id as id,
                    sessionStart,
                    sessionEnd,
                    weekStart,
                    monthStart,
                    weekId,
                    monthId
                    FROM Sessions SC
                    INNER JOIN Weeks WC ON (SC.weekId = WC.id)
                    INNER JOIN Months MC ON (SC.monthId = MC.id)
                    WHERE (sessionEnd>=%s AND sessionStart<=%s)
                    <TOURSELECT>"""
                    
        self.query['select_W'] = """
                    SELECT id
                    FROM Weeks
                    WHERE weekStart = %s"""
        
        self.query['select_M'] = """
                    SELECT id
                    FROM Months
                    WHERE monthStart = %s"""
                    
        self.query['select_SC'] = """
                    SELECT id,
                    sessionId,
                    startTime,
                    endTime,
                    n,
                    street0VPIChance,
                    street0VPI,
                    street0AggrChance,
                    street0Aggr,
                    street0CalledRaiseChance,
                    street0CalledRaiseDone,
                    street0_2BChance,
                    street0_2BDone,
                    street0_3BChance,
                    street0_3BDone,
                    street0_4BChance,
                    street0_4BDone,
                    street0_C4BChance,
                    street0_C4BDone,
                    street0_FoldTo2BChance,
                    street0_FoldTo2BDone,
                    street0_FoldTo3BChance,
                    street0_FoldTo3BDone,
                    street0_FoldTo4BChance,
                    street0_FoldTo4BDone,
                    street0_SqueezeChance,
                    street0_SqueezeDone,
                    raiseToStealChance,
                    raiseToStealDone,
                    stealChance,
                    stealDone,
                    success_Steal,
                    street1Seen,
                    street2Seen,
                    street3Seen,
                    street4Seen,
                    sawShowdown,
                    street1Aggr,
                    street2Aggr,
                    street3Aggr,
                    street4Aggr,
                    otherRaisedStreet0,
                    otherRaisedStreet1,
                    otherRaisedStreet2,
                    otherRaisedStreet3,
                    otherRaisedStreet4,
                    foldToOtherRaisedStreet0,
                    foldToOtherRaisedStreet1,
                    foldToOtherRaisedStreet2,
                    foldToOtherRaisedStreet3,
                    foldToOtherRaisedStreet4,
                    wonWhenSeenStreet1,
                    wonWhenSeenStreet2,
                    wonWhenSeenStreet3,
                    wonWhenSeenStreet4,
                    wonAtSD,
                    raiseFirstInChance,
                    raisedFirstIn,
                    foldBbToStealChance,
                    foldedBbToSteal,
                    foldSbToStealChance,
                    foldedSbToSteal,
                    street1CBChance,
                    street1CBDone,
                    street2CBChance,
                    street2CBDone,
                    street3CBChance,
                    street3CBDone,
                    street4CBChance,
                    street4CBDone,
                    foldToStreet1CBChance,
                    foldToStreet1CBDone,
                    foldToStreet2CBChance,
                    foldToStreet2CBDone,
                    foldToStreet3CBChance,
                    foldToStreet3CBDone,
                    foldToStreet4CBChance,
                    foldToStreet4CBDone,
                    common,
                    committed,
                    winnings,
                    rake,
                    rakeDealt,
                    rakeContributed,
                    rakeWeighted,
                    totalProfit,
                    allInEV,
                    showdownWinnings,
                    nonShowdownWinnings,
                    street1CheckCallRaiseChance,
                    street1CheckCallDone,
                    street1CheckRaiseDone,
                    street2CheckCallRaiseChance,
                    street2CheckCallDone,
                    street2CheckRaiseDone,
                    street3CheckCallRaiseChance,
                    street3CheckCallDone,
                    street3CheckRaiseDone,
                    street4CheckCallRaiseChance,
                    street4CheckCallDone,
                    street4CheckRaiseDone,
                    street0Calls,
                    street1Calls,
                    street2Calls,
                    street3Calls,
                    street4Calls,
                    street0Bets,
                    street1Bets,
                    street2Bets,
                    street3Bets,
                    street4Bets,
                    street0Raises,
                    street1Raises,
                    street2Raises,
                    street3Raises,
                    street4Raises,
                    street1Discards,
                    street2Discards,
                    street3Discards
                    FROM SessionsCache
                    WHERE endTime>=%s
                    AND startTime<=%s
                    AND gametypeId=%s
                    AND playerId=%s"""
                    
        self.query['select_TC'] = """
                    SELECT id, startTime, endTime
                    FROM TourneysCache TC
                    WHERE tourneyId=%s
                    AND playerId=%s"""
                    
        ####################################
        # insert
        ####################################
        
        self.query['insert_W'] = """insert into Weeks (
                    weekStart)
                    values (%s)"""
        
        self.query['insert_M'] = """insert into Months (
                    monthStart)
                    values (%s)"""
                            
        self.query['insert_S'] = """insert into Sessions (
                    weekId,
                    monthId,
                    sessionStart,
                    sessionEnd)
                    values (%s, %s, %s, %s)"""
                            
        self.query['insert_SC'] = """insert into SessionsCache (
                    sessionId,
                    startTime,
                    endTime,
                    gametypeId,
                    playerId,
                    n,
                    street0VPIChance,
                    street0VPI,
                    street0AggrChance,
                    street0Aggr,
                    street0CalledRaiseChance,
                    street0CalledRaiseDone,
                    street0_2BChance,
                    street0_2BDone,
                    street0_3BChance,
                    street0_3BDone,
                    street0_4BChance,
                    street0_4BDone,
                    street0_C4BChance,
                    street0_C4BDone,
                    street0_FoldTo2BChance,
                    street0_FoldTo2BDone,
                    street0_FoldTo3BChance,
                    street0_FoldTo3BDone,
                    street0_FoldTo4BChance,
                    street0_FoldTo4BDone,
                    street0_SqueezeChance,
                    street0_SqueezeDone,
                    raiseToStealChance,
                    raiseToStealDone,
                    stealChance,
                    stealDone,
                    success_Steal,
                    street1Seen,
                    street2Seen,
                    street3Seen,
                    street4Seen,
                    sawShowdown,
                    street1Aggr,
                    street2Aggr,
                    street3Aggr,
                    street4Aggr,
                    otherRaisedStreet0,
                    otherRaisedStreet1,
                    otherRaisedStreet2,
                    otherRaisedStreet3,
                    otherRaisedStreet4,
                    foldToOtherRaisedStreet0,
                    foldToOtherRaisedStreet1,
                    foldToOtherRaisedStreet2,
                    foldToOtherRaisedStreet3,
                    foldToOtherRaisedStreet4,
                    wonWhenSeenStreet1,
                    wonWhenSeenStreet2,
                    wonWhenSeenStreet3,
                    wonWhenSeenStreet4,
                    wonAtSD,
                    raiseFirstInChance,
                    raisedFirstIn,
                    foldBbToStealChance,
                    foldedBbToSteal,
                    foldSbToStealChance,
                    foldedSbToSteal,
                    street1CBChance,
                    street1CBDone,
                    street2CBChance,
                    street2CBDone,
                    street3CBChance,
                    street3CBDone,
                    street4CBChance,
                    street4CBDone,
                    foldToStreet1CBChance,
                    foldToStreet1CBDone,
                    foldToStreet2CBChance,
                    foldToStreet2CBDone,
                    foldToStreet3CBChance,
                    foldToStreet3CBDone,
                    foldToStreet4CBChance,
                    foldToStreet4CBDone,
                    common,
                    committed,
                    winnings,
                    rake,
                    rakeDealt,
                    rakeContributed,
                    rakeWeighted,
                    totalProfit,
                    allInEV,
                    showdownWinnings,
                    nonShowdownWinnings,
                    street1CheckCallRaiseChance,
                    street1CheckCallDone,
                    street1CheckRaiseDone,
                    street2CheckCallRaiseChance,
                    street2CheckCallDone,
                    street2CheckRaiseDone,
                    street3CheckCallRaiseChance,
                    street3CheckCallDone,
                    street3CheckRaiseDone,
                    street4CheckCallRaiseChance,
                    street4CheckCallDone,
                    street4CheckRaiseDone,
                    street0Calls,
                    street1Calls,
                    street2Calls,
                    street3Calls,
                    street4Calls,
                    street0Bets,
                    street1Bets,
                    street2Bets,
                    street3Bets,
                    street4Bets,
                    street0Raises,
                    street1Raises,
                    street2Raises,
                    street3Raises,
                    street4Raises,
                    street1Discards,
                    street2Discards,
                    street3Discards
                    )
                    values (%s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s)"""
                            
        self.query['insert_TC'] = """insert into TourneysCache (
                    sessionId,
                    startTime,
                    endTime,
                    tourneyId,
                    playerId,
                    n,
                    street0VPIChance,
                    street0VPI,
                    street0AggrChance,
                    street0Aggr,
                    street0CalledRaiseChance,
                    street0CalledRaiseDone,
                    street0_2BChance,
                    street0_2BDone,
                    street0_3BChance,
                    street0_3BDone,
                    street0_4BChance,
                    street0_4BDone,
                    street0_C4BChance,
                    street0_C4BDone,
                    street0_FoldTo2BChance,
                    street0_FoldTo2BDone,
                    street0_FoldTo3BChance,
                    street0_FoldTo3BDone,
                    street0_FoldTo4BChance,
                    street0_FoldTo4BDone,
                    street0_SqueezeChance,
                    street0_SqueezeDone,
                    raiseToStealChance,
                    raiseToStealDone,
                    stealChance,
                    stealDone,
                    success_Steal,
                    street1Seen,
                    street2Seen,
                    street3Seen,
                    street4Seen,
                    sawShowdown,
                    street1Aggr,
                    street2Aggr,
                    street3Aggr,
                    street4Aggr,
                    otherRaisedStreet0,
                    otherRaisedStreet1,
                    otherRaisedStreet2,
                    otherRaisedStreet3,
                    otherRaisedStreet4,
                    foldToOtherRaisedStreet0,
                    foldToOtherRaisedStreet1,
                    foldToOtherRaisedStreet2,
                    foldToOtherRaisedStreet3,
                    foldToOtherRaisedStreet4,
                    wonWhenSeenStreet1,
                    wonWhenSeenStreet2,
                    wonWhenSeenStreet3,
                    wonWhenSeenStreet4,
                    wonAtSD,
                    raiseFirstInChance,
                    raisedFirstIn,
                    foldBbToStealChance,
                    foldedBbToSteal,
                    foldSbToStealChance,
                    foldedSbToSteal,
                    street1CBChance,
                    street1CBDone,
                    street2CBChance,
                    street2CBDone,
                    street3CBChance,
                    street3CBDone,
                    street4CBChance,
                    street4CBDone,
                    foldToStreet1CBChance,
                    foldToStreet1CBDone,
                    foldToStreet2CBChance,
                    foldToStreet2CBDone,
                    foldToStreet3CBChance,
                    foldToStreet3CBDone,
                    foldToStreet4CBChance,
                    foldToStreet4CBDone,
                    common,
                    committed,
                    winnings,
                    rake,
                    rakeDealt,
                    rakeContributed,
                    rakeWeighted,
                    totalProfit,
                    allInEV,
                    showdownWinnings,
                    nonShowdownWinnings,
                    street1CheckCallRaiseChance,
                    street1CheckCallDone,
                    street1CheckRaiseDone,
                    street2CheckCallRaiseChance,
                    street2CheckCallDone,
                    street2CheckRaiseDone,
                    street3CheckCallRaiseChance,
                    street3CheckCallDone,
                    street3CheckRaiseDone,
                    street4CheckCallRaiseChance,
                    street4CheckCallDone,
                    street4CheckRaiseDone,
                    street0Calls,
                    street1Calls,
                    street2Calls,
                    street3Calls,
                    street4Calls,
                    street0Bets,
                    street1Bets,
                    street2Bets,
                    street3Bets,
                    street4Bets,
                    street0Raises,
                    street1Raises,
                    street2Raises,
                    street3Raises,
                    street4Raises,
                    street1Discards,
                    street2Discards,
                    street3Discards
                    )
                    values (%s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s)"""
                    
        ####################################
        # update
        ####################################
        
        self.query['update_WM_S'] = """
                    UPDATE Sessions SET
                    weekId=%s,
                    monthId=%s
                    WHERE id=%s"""
                    
        self.query['update_S'] = """
                    UPDATE Sessions SET 
                    weekId=%s,
                    monthId=%s,
                    sessionStart=%s,
                    sessionEnd=%s
                    WHERE id=%s"""
                    
        self.query['update_SC'] = """
                    UPDATE SessionsCache SET
                    startTime=%s,
                    endTime=%s,
                    n=n+%s,
                    street0VPIChance=street0VPIChance+%s,
                    street0VPI=street0VPI+%s,
                    street0AggrChance=street0AggrChance+%s,
                    street0Aggr=street0Aggr+%s,
                    street0CalledRaiseChance=street0CalledRaiseChance+%s,
                    street0CalledRaiseDone=street0CalledRaiseDone+%s,
                    street0_2BChance=street0_2BChance+%s,
                    street0_2BDone=street0_2BDone+%s,
                    street0_3BChance=street0_3BChance+%s,
                    street0_3BDone=street0_3BDone+%s,
                    street0_4BChance=street0_4BChance+%s,
                    street0_4BDone=street0_4BDone+%s,
                    street0_C4BChance=street0_C4BChance+%s,
                    street0_C4BDone=street0_C4BDone+%s,
                    street0_FoldTo2BChance=street0_FoldTo2BChance+%s,
                    street0_FoldTo2BDone=street0_FoldTo2BDone+%s,
                    street0_FoldTo3BChance=street0_FoldTo3BChance+%s,
                    street0_FoldTo3BDone=street0_FoldTo3BDone+%s,
                    street0_FoldTo4BChance=street0_FoldTo4BChance+%s,
                    street0_FoldTo4BDone=street0_FoldTo4BDone+%s,
                    street0_SqueezeChance=street0_SqueezeChance+%s,
                    street0_SqueezeDone=street0_SqueezeDone+%s,
                    raiseToStealChance=raiseToStealChance+%s,
                    raiseToStealDone=raiseToStealDone+%s,
                    stealChance=stealChance+%s,
                    stealDone=stealDone+%s,
                    success_Steal=success_Steal+%s,
                    street1Seen=street1Seen+%s,
                    street2Seen=street2Seen+%s,
                    street3Seen=street3Seen+%s,
                    street4Seen=street4Seen+%s,
                    sawShowdown=sawShowdown+%s,
                    street1Aggr=street1Aggr+%s,
                    street2Aggr=street2Aggr+%s,
                    street3Aggr=street3Aggr+%s,
                    street4Aggr=street4Aggr+%s,
                    otherRaisedStreet0=otherRaisedStreet0+%s,
                    otherRaisedStreet1=otherRaisedStreet1+%s,
                    otherRaisedStreet2=otherRaisedStreet2+%s,
                    otherRaisedStreet3=otherRaisedStreet3+%s,
                    otherRaisedStreet4=otherRaisedStreet4+%s,
                    foldToOtherRaisedStreet0=foldToOtherRaisedStreet0+%s,
                    foldToOtherRaisedStreet1=foldToOtherRaisedStreet1+%s,
                    foldToOtherRaisedStreet2=foldToOtherRaisedStreet2+%s,
                    foldToOtherRaisedStreet3=foldToOtherRaisedStreet3+%s,
                    foldToOtherRaisedStreet4=foldToOtherRaisedStreet4+%s,
                    wonWhenSeenStreet1=wonWhenSeenStreet1+%s,
                    wonWhenSeenStreet2=wonWhenSeenStreet2+%s,
                    wonWhenSeenStreet3=wonWhenSeenStreet3+%s,
                    wonWhenSeenStreet4=wonWhenSeenStreet4+%s,
                    wonAtSD=wonAtSD+%s,
                    raiseFirstInChance=raiseFirstInChance+%s,
                    raisedFirstIn=raisedFirstIn+%s,
                    foldBbToStealChance=foldBbToStealChance+%s,
                    foldedBbToSteal=foldedBbToSteal+%s,
                    foldSbToStealChance=foldSbToStealChance+%s,
                    foldedSbToSteal=foldedSbToSteal+%s,
                    street1CBChance=street1CBChance+%s,
                    street1CBDone=street1CBDone+%s,
                    street2CBChance=street2CBChance+%s,
                    street2CBDone=street2CBDone+%s,
                    street3CBChance=street3CBChance+%s,
                    street3CBDone=street3CBDone+%s,
                    street4CBChance=street4CBChance+%s,
                    street4CBDone=street4CBDone+%s,
                    foldToStreet1CBChance=foldToStreet1CBChance+%s,
                    foldToStreet1CBDone=foldToStreet1CBDone+%s,
                    foldToStreet2CBChance=foldToStreet2CBChance+%s,
                    foldToStreet2CBDone=foldToStreet2CBDone+%s,
                    foldToStreet3CBChance=foldToStreet3CBChance+%s,
                    foldToStreet3CBDone=foldToStreet3CBDone+%s,
                    foldToStreet4CBChance=foldToStreet4CBChance+%s,
                    foldToStreet4CBDone=foldToStreet4CBDone+%s,
                    common=common+%s,
                    committed=committed+%s,
                    winnings=winnings+%s,
                    rake=rake+%s,
                    rakeDealt=rakeDealt+%s,
                    rakeContributed=rakeContributed+%s,
                    rakeWeighted=rakeWeighted+%s,
                    totalProfit=totalProfit+%s,
                    allInEV=allInEV+%s,
                    showdownWinnings=showdownWinnings+%s,
                    nonShowdownWinnings=nonShowdownWinnings+%s,
                    street1CheckCallRaiseChance=street1CheckCallRaiseChance+%s,
                    street1CheckCallDone=street1CheckCallDone+%s,
                    street1CheckRaiseDone=street1CheckRaiseDone+%s,
                    street2CheckCallRaiseChance=street2CheckCallRaiseChance+%s,
                    street2CheckCallDone=street2CheckCallDone+%s,
                    street2CheckRaiseDone=street2CheckRaiseDone+%s,
                    street3CheckCallRaiseChance=street3CheckCallRaiseChance+%s,
                    street3CheckCallDone=street3CheckCallDone+%s,
                    street3CheckRaiseDone=street3CheckRaiseDone+%s,
                    street4CheckCallRaiseChance=street4CheckCallRaiseChance+%s,
                    street4CheckCallDone=street4CheckCallDone+%s,
                    street4CheckRaiseDone=street4CheckRaiseDone+%s,
                    street0Calls=street0Calls+%s,
                    street1Calls=street1Calls+%s,
                    street2Calls=street2Calls+%s,
                    street3Calls=street3Calls+%s,
                    street4Calls=street4Calls+%s,
                    street0Bets=street0Bets+%s, 
                    street1Bets=street1Bets+%s,
                    street2Bets=street2Bets+%s, 
                    street3Bets=street3Bets+%s,
                    street4Bets=street4Bets+%s, 
                    street0Raises=street0Raises+%s,
                    street1Raises=street1Raises+%s,
                    street2Raises=street2Raises+%s,
                    street3Raises=street3Raises+%s,
                    street4Raises=street4Raises+%s,
                    street1Discards=street1Discards+%s,
                    street2Discards=street2Discards+%s,
                    street3Discards=street3Discards+%s
                    WHERE id=%s"""
                    
        self.query['update_TC'] = """
                    UPDATE TourneysCache SET
                    <UPDATE>
                    n=n+%s,
                    street0VPIChance=street0VPIChance+%s,
                    street0VPI=street0VPI+%s,
                    street0AggrChance=street0AggrChance+%s,
                    street0Aggr=street0Aggr+%s,
                    street0CalledRaiseChance=street0CalledRaiseChance+%s,
                    street0CalledRaiseDone=street0CalledRaiseDone+%s,
                    street0_2BChance=street0_2BChance+%s,
                    street0_2BDone=street0_2BDone+%s,
                    street0_3BChance=street0_3BChance+%s,
                    street0_3BDone=street0_3BDone+%s,
                    street0_4BChance=street0_4BChance+%s,
                    street0_4BDone=street0_4BDone+%s,
                    street0_C4BChance=street0_C4BChance+%s,
                    street0_C4BDone=street0_C4BDone+%s,
                    street0_FoldTo2BChance=street0_FoldTo2BChance+%s,
                    street0_FoldTo2BDone=street0_FoldTo2BDone+%s,
                    street0_FoldTo3BChance=street0_FoldTo3BChance+%s,
                    street0_FoldTo3BDone=street0_FoldTo3BDone+%s,
                    street0_FoldTo4BChance=street0_FoldTo4BChance+%s,
                    street0_FoldTo4BDone=street0_FoldTo4BDone+%s,
                    street0_SqueezeChance=street0_SqueezeChance+%s,
                    street0_SqueezeDone=street0_SqueezeDone+%s,
                    raiseToStealChance=raiseToStealChance+%s,
                    raiseToStealDone=raiseToStealDone+%s,
                    stealChance=stealChance+%s,
                    stealDone=stealDone+%s,
                    success_Steal=success_Steal+%s,
                    street1Seen=street1Seen+%s,
                    street2Seen=street2Seen+%s,
                    street3Seen=street3Seen+%s,
                    street4Seen=street4Seen+%s,
                    sawShowdown=sawShowdown+%s,
                    street1Aggr=street1Aggr+%s,
                    street2Aggr=street2Aggr+%s,
                    street3Aggr=street3Aggr+%s,
                    street4Aggr=street4Aggr+%s,
                    otherRaisedStreet0=otherRaisedStreet0+%s,
                    otherRaisedStreet1=otherRaisedStreet1+%s,
                    otherRaisedStreet2=otherRaisedStreet2+%s,
                    otherRaisedStreet3=otherRaisedStreet3+%s,
                    otherRaisedStreet4=otherRaisedStreet4+%s,
                    foldToOtherRaisedStreet0=foldToOtherRaisedStreet0+%s,
                    foldToOtherRaisedStreet1=foldToOtherRaisedStreet1+%s,
                    foldToOtherRaisedStreet2=foldToOtherRaisedStreet2+%s,
                    foldToOtherRaisedStreet3=foldToOtherRaisedStreet3+%s,
                    foldToOtherRaisedStreet4=foldToOtherRaisedStreet4+%s,
                    wonWhenSeenStreet1=wonWhenSeenStreet1+%s,
                    wonWhenSeenStreet2=wonWhenSeenStreet2+%s,
                    wonWhenSeenStreet3=wonWhenSeenStreet3+%s,
                    wonWhenSeenStreet4=wonWhenSeenStreet4+%s,
                    wonAtSD=wonAtSD+%s,
                    raiseFirstInChance=raiseFirstInChance+%s,
                    raisedFirstIn=raisedFirstIn+%s,
                    foldBbToStealChance=foldBbToStealChance+%s,
                    foldedBbToSteal=foldedBbToSteal+%s,
                    foldSbToStealChance=foldSbToStealChance+%s,
                    foldedSbToSteal=foldedSbToSteal+%s,
                    street1CBChance=street1CBChance+%s,
                    street1CBDone=street1CBDone+%s,
                    street2CBChance=street2CBChance+%s,
                    street2CBDone=street2CBDone+%s,
                    street3CBChance=street3CBChance+%s,
                    street3CBDone=street3CBDone+%s,
                    street4CBChance=street4CBChance+%s,
                    street4CBDone=street4CBDone+%s,
                    foldToStreet1CBChance=foldToStreet1CBChance+%s,
                    foldToStreet1CBDone=foldToStreet1CBDone+%s,
                    foldToStreet2CBChance=foldToStreet2CBChance+%s,
                    foldToStreet2CBDone=foldToStreet2CBDone+%s,
                    foldToStreet3CBChance=foldToStreet3CBChance+%s,
                    foldToStreet3CBDone=foldToStreet3CBDone+%s,
                    foldToStreet4CBChance=foldToStreet4CBChance+%s,
                    foldToStreet4CBDone=foldToStreet4CBDone+%s,
                    common=common+%s,
                    committed=committed+%s,
                    winnings=winnings+%s,
                    rake=rake+%s,
                    rakeDealt=rakeDealt+%s,
                    rakeContributed=rakeContributed+%s,
                    rakeWeighted=rakeWeighted+%s,
                    totalProfit=totalProfit+%s,
                    allInEV=allInEV+%s,
                    showdownWinnings=showdownWinnings+%s,
                    nonShowdownWinnings=nonShowdownWinnings+%s,
                    street1CheckCallRaiseChance=street1CheckCallRaiseChance+%s,
                    street1CheckCallDone=street1CheckCallDone+%s,
                    street1CheckRaiseDone=street1CheckRaiseDone+%s,
                    street2CheckCallRaiseChance=street2CheckCallRaiseChance+%s,
                    street2CheckCallDone=street2CheckCallDone+%s,
                    street2CheckRaiseDone=street2CheckRaiseDone+%s,
                    street3CheckCallRaiseChance=street3CheckCallRaiseChance+%s,
                    street3CheckCallDone=street3CheckCallDone+%s,
                    street3CheckRaiseDone=street3CheckRaiseDone+%s,
                    street4CheckCallRaiseChance=street4CheckCallRaiseChance+%s,
                    street4CheckCallDone=street4CheckCallDone+%s,
                    street4CheckRaiseDone=street4CheckRaiseDone+%s,
                    street0Calls=street0Calls+%s,
                    street1Calls=street1Calls+%s,
                    street2Calls=street2Calls+%s,
                    street3Calls=street3Calls+%s,
                    street4Calls=street4Calls+%s,
                    street0Bets=street0Bets+%s, 
                    street1Bets=street1Bets+%s,
                    street2Bets=street2Bets+%s, 
                    street3Bets=street3Bets+%s,
                    street4Bets=street4Bets+%s, 
                    street0Raises=street0Raises+%s,
                    street1Raises=street1Raises+%s,
                    street2Raises=street2Raises+%s,
                    street3Raises=street3Raises+%s,
                    street4Raises=street4Raises+%s,
                    street1Discards=street1Discards+%s,
                    street2Discards=street2Discards+%s,
                    street3Discards=street3Discards+%s
                    WHERE tourneyId=%s
                    AND playerId=%s"""
                    
        ####################################
        # delete
        ####################################
                    
        self.query['delete_S'] = """
                    DELETE FROM Sessions
                    WHERE id=%s"""
                    
        self.query['delete_SC'] = """
                    DELETE FROM SessionsCache
                    WHERE id=%s"""
                    
        ####################################
        # update SessionsCache, Hands, Tourneys
        ####################################
                    
        self.query['update_S_SC'] = """
                    UPDATE SessionsCache SET
                    sessionId=%s
                    WHERE sessionId=%s"""
                    
        self.query['update_S_TC'] = """
                    UPDATE TourneysCache SET
                    sessionId=%s
                    WHERE sessionId=%s"""
                    
        self.query['update_S_T'] = """
                    UPDATE Tourneys SET
                    sessionId=%s
                    WHERE sessionId=%s"""
                            
        self.query['update_S_H'] = """
                    UPDATE Hands SET
                    sessionId=%s
                    WHERE sessionId=%s"""
                    
        ####################################
        # update Tourneys w. sessionIds, hands, start/end
        ####################################
                    
        self.query['updateTourneysSessions'] = """
                    UPDATE Tourneys SET
                    sessionId=%s
                    WHERE id=%s"""
        
        ####################################
        # Database management queries
        ####################################

        self.query['analyze'] = "analyze"
            

        self.query['lockForInsert'] = ""

        self.query['getGametypeFL'] = """SELECT id
                                           FROM Gametypes
                                           WHERE siteId=%s
                                           AND   type=%s
                                           AND   category=%s
                                           AND   limitType=%s
                                           AND   smallBet=%s
                                           AND   bigBet=%s
                                           AND   maxSeats=%s
                                           AND   ante=%s
        """ #TODO: seems odd to have limitType variable in this query

        self.query['getGametypeNL'] = """SELECT id
                                           FROM Gametypes
                                           WHERE siteId=%s
                                           AND   type=%s
                                           AND   category=%s
                                           AND   limitType=%s
                                           AND   currency=%s
                                           AND   mix=%s
                                           AND   smallBlind=%s
                                           AND   bigBlind=%s
                                           AND   maxSeats=%s
                                           AND   ante=%s
                                           AND   buyinType=%s
                                           AND   fast=%s
                                           AND   newToGame=%s
                                           AND   homeGame=%s
                                           AND   split=%s
        """ #TODO: seems odd to have limitType variable in this query

        self.query['insertGameTypes'] = """insert into Gametypes (siteId, currency, type, base, category, limitType, hiLo, mix, 
                                               smallBlind, bigBlind, smallBet, bigBet, maxSeats, ante, buyinType, fast, newToGame, homeGame, split)
                                           values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        self.query['isAlreadyInDB'] = """SELECT H.id FROM Hands H
                                         INNER JOIN Gametypes G ON (H.gametypeId = G.id)
                                         WHERE siteHandNo=%s AND G.siteId=%s<heroSeat>
        """
        
        self.query['getTourneyTypeIdByTourneyNo'] = """SELECT tt.id,
                                                              tt.siteId,
                                                              tt.currency,
                                                              tt.buyin,
                                                              tt.fee,
                                                              tt.category,
                                                              tt.limitType,
                                                              tt.maxSeats,
                                                              tt.sng,
                                                              tt.knockout,
                                                              tt.koBounty,
                                                              tt.progressive,
                                                              tt.rebuy,
                                                              tt.rebuyCost,
                                                              tt.addOn,
                                                              tt.addOnCost,
                                                              tt.speed,
                                                              tt.shootout,
                                                              tt.matrix,
                                                              tt.fast,
                                                              tt.stack, 
                                                              tt.step,
                                                              tt.stepNo,
                                                              tt.chance,
                                                              tt.chanceCount,
                                                              tt.multiEntry,
                                                              tt.reEntry,
                                                              tt.homeGame,
                                                              tt.newToGame,
                                                              tt.split,
                                                              tt.fifty50,
                                                              tt.time,
                                                              tt.timeAmt,
                                                              tt.satellite,
                                                              tt.doubleOrNothing,
                                                              tt.cashOut,
                                                              tt.onDemand,
                                                              tt.flighted,
                                                              tt.guarantee,
                                                              tt.guaranteeAmt
                                                    FROM TourneyTypes tt 
                                                    INNER JOIN Tourneys t ON (t.tourneyTypeId = tt.id) 
                                                    WHERE t.siteTourneyNo=%s AND tt.siteId=%s
        """
        
        self.query['getTourneyTypeId'] = """SELECT  id
                                            FROM TourneyTypes
                                            WHERE siteId=%s
                                            AND currency=%s
                                            AND buyin=%s
                                            AND fee=%s
                                            AND category=%s
                                            AND limitType=%s
                                            AND maxSeats=%s
                                            AND sng=%s
                                            AND knockout=%s
                                            AND koBounty=%s
                                            AND progressive=%s
                                            AND rebuy=%s
                                            AND rebuyCost=%s
                                            AND addOn=%s
                                            AND addOnCost=%s
                                            AND speed=%s
                                            AND shootout=%s
                                            AND matrix=%s
                                            AND fast=%s
                                            AND stack=%s
                                            AND step=%s
                                            AND stepNo=%s
                                            AND chance=%s
                                            AND chanceCount=%s
                                            AND multiEntry=%s
                                            AND reEntry=%s
                                            AND homeGame=%s
                                            AND newToGame=%s
                                            AND split=%s
                                            AND fifty50=%s
                                            AND time=%s
                                            AND timeAmt=%s
                                            AND satellite=%s
                                            AND doubleOrNothing=%s
                                            AND cashOut=%s
                                            AND onDemand=%s
                                            AND flighted=%s
                                            AND guarantee=%s
                                            AND guaranteeAmt=%s
        """

        self.query['insertTourneyType'] = """insert into TourneyTypes (
                                                   siteId, currency, buyin, fee, category, limitType, maxSeats, sng, knockout, koBounty, progressive,
                                                   rebuy, rebuyCost, addOn, addOnCost, speed, shootout, matrix, fast,
                                                   stack, step, stepNo, chance, chanceCount, multiEntry, reEntry, homeGame, newToGame, split,
                                                   fifty50, time, timeAmt, satellite, doubleOrNothing, cashOut, onDemand, flighted, guarantee, guaranteeAmt
                                                   )
                                              values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                                      %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        self.query['updateTourneyTypeId'] = """UPDATE Tourneys
                                            SET tourneyTypeId = %s
                                            WHERE tourneyTypeId in (SELECT id FROM TourneyTypes WHERE siteId=%s)
                                            AND siteTourneyNo=%s
        """
        
        self.query['selectTourneyWithTypeId'] = """SELECT id 
                                                FROM Tourneys
                                                WHERE tourneyTypeId = %s
        """
        
        self.query['deleteTourneyTypeId'] = """DELETE FROM TourneyTypes WHERE id = %s
        """

        self.query['getTourneyByTourneyNo'] = """SELECT t.*
                                        FROM Tourneys t
                                        INNER JOIN TourneyTypes tt ON (t.tourneyTypeId = tt.id)
                                        WHERE tt.siteId=%s AND t.siteTourneyNo=%s
        """

        self.query['getTourneyInfo'] = """SELECT tt.*, t.*
                                        FROM Tourneys t
                                        INNER JOIN TourneyTypes tt ON (t.tourneyTypeId = tt.id)
                                        INNER JOIN Sites s ON (tt.siteId = s.id)
                                        WHERE s.name=%s AND t.siteTourneyNo=%s
        """

        self.query['getSiteTourneyNos'] = """SELECT t.siteTourneyNo
                                        FROM Tourneys t
                                        INNER JOIN TourneyTypes tt ON (t.tourneyTypeId = tt.id)
                                        INNER JOIN Sites s ON (tt.siteId = s.id)
                                        WHERE tt.siteId=%s
        """

        self.query['getTourneyPlayerInfo'] = """SELECT tp.*
                                        FROM Tourneys t
                                        INNER JOIN TourneyTypes tt ON (t.tourneyTypeId = tt.id)
                                        INNER JOIN Sites s ON (tt.siteId = s.id)
                                        INNER JOIN TourneysPlayers tp ON (tp.tourneyId = t.id)
                                        INNER JOIN Players p ON (p.id = tp.playerId)
                                        WHERE s.name=%s AND t.siteTourneyNo=%s AND p.name=%s
        """
        
        self.query['insertTourney'] = """insert into Tourneys (
                                             tourneyTypeId, sessionId, siteTourneyNo, entries, prizepool,
                                             startTime, endTime, tourneyName, totalRebuyCount, totalAddOnCount,
                                             comment, commentTs, added, addedCurrency)
                                        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        self.query['updateTourney'] = """UPDATE Tourneys
                                             SET entries = %s,
                                                 prizepool = %s,
                                                 startTime = %s,
                                                 endTime = %s,
                                                 tourneyName = %s,
                                                 totalRebuyCount = %s,
                                                 totalAddOnCount = %s,
                                                 comment = %s,
                                                 commentTs = %s,
                                                 added = %s,
                                                 addedCurrency = %s
                                        WHERE id=%s
        """
        
        self.query['updateTourneyStart'] = """UPDATE Tourneys
                                             SET startTime = %s
                                        WHERE id=%s
        """
        
        self.query['updateTourneyEnd'] = """UPDATE Tourneys
                                             SET endTime = %s
                                        WHERE id=%s
        """
        
        self.query['getTourneysPlayersByIds'] = """SELECT *
                                                FROM TourneysPlayers
                                                WHERE tourneyId=%s AND playerId=%s AND entryId=%s
        """
        
        self.query['getTourneysPlayersByTourney'] = """SELECT playerId, entryId
                                                       FROM TourneysPlayers
                                                       WHERE tourneyId=%s
        """

        self.query['updateTourneysPlayer'] = """UPDATE TourneysPlayers
                                                 SET rank = %s,
                                                     winnings = %s,
                                                     winningsCurrency = %s,
                                                     rebuyCount = %s,
                                                     addOnCount = %s,
                                                     koCount = %s
                                                 WHERE id=%s
        """

        self.query['updateTourneysPlayerBounties'] = """UPDATE TourneysPlayers
                                                 SET koCount = case when koCount is null then %s else koCount+%s end
                                                 WHERE id=%s
        """

        self.query['insertTourneysPlayer'] = """insert into TourneysPlayers (
                                                    tourneyId,
                                                    playerId,
                                                    entryId,
                                                    rank,
                                                    winnings,
                                                    winningsCurrency,
                                                    rebuyCount,
                                                    addOnCount,
                                                    koCount
                                                )
                                                values (%s, %s, %s, %s, %s, 
                                                        %s, %s, %s, %s)
        """

        self.query['selectHandsPlayersWithWrongTTypeId'] = """SELECT id
                                                              FROM HandsPlayers 
                                                              WHERE tourneyTypeId <> %s AND (TourneysPlayersId+0=%s)
        """

#            self.query['updateHandsPlayersForTTypeId2'] = """UPDATE HandsPlayers 
#                                                            SET tourneyTypeId= %s
#                                                            WHERE (TourneysPlayersId+0=%s)
#            """

        self.query['updateHandsPlayersForTTypeId'] = """UPDATE HandsPlayers 
                                                         SET tourneyTypeId= %s
                                                         WHERE (id=%s)
        """


        self.query['handsPlayersTTypeId_joiner'] = " OR TourneysPlayersId+0="
        self.query['handsPlayersTTypeId_joiner_id'] = " OR id="

        self.query['store_hand'] = """insert into Hands (
                                            tablename,
                                            sitehandno,
                                            tourneyId,
                                            gametypeid,
                                            sessionId,
                                            fileId,
                                            startTime,
                                            importtime,
                                            seats,
                                            heroSeat,
                                            maxPosition,
                                            texture,
                                            playersVpi,
                                            boardcard1,
                                            boardcard2,
                                            boardcard3,
                                            boardcard4,
                                            boardcard5,
                                            runItTwice,
                                            playersAtStreet1,
                                            playersAtStreet2,
                                            playersAtStreet3,
                                            playersAtStreet4,
                                            playersAtShowdown,
                                            street0Raises,
                                            street1Raises,
                                            street2Raises,
                                            street3Raises,
                                            street4Raises,
                                            street0Pot,
                                            street1Pot,
                                            street2Pot,
                                            street3Pot,
                                            street4Pot,
                                            finalPot
                                             )
                                             values
                                              (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                               %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                               %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                               %s, %s)"""


        self.query['store_hands_players'] = """insert into HandsPlayers (
                handId,
                playerId,
                startCash,
                effStack,
                startBounty,
                endBounty,
                seatNo,
                sitout,
                card1,
                card2,
                card3,
                card4,
                card5,
                card6,
                card7,
                card8,
                card9,
                card10,
                card11,
                card12,
                card13,
                card14,
                card15,
                card16,
                card17,
                card18,
                card19,
                card20,
                common,
                committed,
                winnings,
                rake,
                rakeDealt,
                rakeContributed,
                rakeWeighted,
                totalProfit,
                allInEV,
                street0VPIChance,
                street0VPI,
                street1Seen,
                street2Seen,
                street3Seen,
                street4Seen,
                sawShowdown,
                showed,
                street0AllIn,
                street1AllIn,
                street2AllIn,
                street3AllIn,
                street4AllIn,
                wentAllIn,
                street0AggrChance,
                street0Aggr,
                street1Aggr,
                street2Aggr,
                street3Aggr,
                street4Aggr,
                street1CBChance,
                street2CBChance,
                street3CBChance,
                street4CBChance,
                street1CBDone,
                street2CBDone,
                street3CBDone,
                street4CBDone,
                wonWhenSeenStreet1,
                wonWhenSeenStreet2,
                wonWhenSeenStreet3,
                wonWhenSeenStreet4,
                wonAtSD,
                position,
                street0InPosition,
                street1InPosition,
                street2InPosition,
                street3InPosition,
                street4InPosition,
                street0FirstToAct,
                street1FirstToAct,
                street2FirstToAct,
                street3FirstToAct,
                street4FirstToAct,
                tourneysPlayersId,
                startCards,
                street0CalledRaiseChance,
                street0CalledRaiseDone,
                street0_2BChance,
                street0_2BDone,
                street0_3BChance,
                street0_3BDone,
                street0_4BChance,
                street0_4BDone,
                street0_C4BChance,
                street0_C4BDone,
                street0_FoldTo2BChance,
                street0_FoldTo2BDone,
                street0_FoldTo3BChance,
                street0_FoldTo3BDone,
                street0_FoldTo4BChance,
                street0_FoldTo4BDone,
                street0_SqueezeChance,
                street0_SqueezeDone,
                raiseToStealChance,
                raiseToStealDone,
                stealChance,
                stealDone,
                success_Steal,
                otherRaisedStreet0,
                otherRaisedStreet1,
                otherRaisedStreet2,
                otherRaisedStreet3,
                otherRaisedStreet4,
                foldToOtherRaisedStreet0,
                foldToOtherRaisedStreet1,
                foldToOtherRaisedStreet2,
                foldToOtherRaisedStreet3,
                foldToOtherRaisedStreet4,
                raiseFirstInChance,
                raisedFirstIn,
                foldBbToStealChance,
                foldedBbToSteal,
                foldSbToStealChance,
                foldedSbToSteal,
                foldToStreet1CBChance,
                foldToStreet1CBDone,
                foldToStreet2CBChance,
                foldToStreet2CBDone,
                foldToStreet3CBChance,
                foldToStreet3CBDone,
                foldToStreet4CBChance,
                foldToStreet4CBDone,
                street1CheckCallRaiseChance,
                street1CheckCallDone,
                street1CheckRaiseDone,
                street2CheckCallRaiseChance,
                street2CheckCallDone,
                street2CheckRaiseDone,
                street3CheckCallRaiseChance,
                street3CheckCallDone,
                street3CheckRaiseDone,
                street4CheckCallRaiseChance,
                street4CheckCallDone,
                street4CheckRaiseDone,
                street0Calls,
                street1Calls,
                street2Calls,
                street3Calls,
                street4Calls,
                street0Bets,
                street1Bets,
                street2Bets,
                street3Bets,
                street4Bets,
                street0Raises,
                street1Raises,
                street2Raises,
                street3Raises,
                street4Raises,
                street1Discards,
                street2Discards,
                street3Discards,
                handString
               )
               values (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s
                )"""

        self.query['store_hands_actions'] = """insert into HandsActions (
                        handId,
                        playerId,
                        street,
                        actionNo,
                        streetActionNo,
                        actionId,
                        amount,
                        raiseTo,
                        amountCalled,
                        numDiscarded,
                        cardsDiscarded,
                        allIn
               )
               values (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s
                )"""

        self.query['store_hands_stove'] = """insert into HandsStove (
                        handId,
                        playerId,
                        streetId,
                        boardId,
                        hiLo,
                        rankId,
                        value,
                        cards,
                        ev
               )
               values (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
               )"""
                
        self.query['store_boards'] = """insert into Boards (
                        handId,
                        boardId,
                        boardcard1,
                        boardcard2,
                        boardcard3,
                        boardcard4,
                        boardcard5
               )
               values (
                    %s, %s, %s, %s, %s,
                    %s, %s
                )"""
                
        self.query['store_hands_pots'] = """insert into HandsPots (
                        handId,
                        potId,
                        boardId,
                        hiLo,
                        playerId,
                        pot,
                        collected,
                        rake
               )
               values (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s
               )"""

        ################################
        # queries for Files Table
        ################################
        
        self.query['get_id'] = """
                        SELECT id
                        FROM Files
                        WHERE file=%s"""
        
        self.query['store_file'] = """  insert into Files (
                        file,
                        site,
                        startTime,
                        lastUpdate,
                        hands,
                        storedHands,
                        dups,
                        partial,
                        skipped,
                        errs,
                        ttime100,
                        finished)
               values (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s
                )"""
        
        self.query['update_file'] = """
                    UPDATE Files SET
                    type=%s,
                    lastUpdate=%s,
                    endTime=%s,
                    hands=hands+%s,
                    storedHands=storedHands+%s,
                    dups=dups+%s,
                    partial=partial+%s,
                    skipped=skipped+%s,
                    errs=errs+%s,
                    ttime100=ttime100+%s,
                    finished=%s
                    WHERE id=%s"""
        
        ################################
        # Counts for DB stats window
        ################################
        self.query['getHandCount'] = "SELECT COUNT(*) FROM Hands"
        self.query['getTourneyCount'] = "SELECT COUNT(*) FROM Tourneys"
        self.query['getTourneyTypeCount'] = "SELECT COUNT(*) FROM TourneyTypes"
        
        ################################
        # queries for dumpDatabase
        ################################
        for table in (u'Autorates', u'Backings', u'Gametypes', u'Hands', u'HandsActions', u'HandsPlayers', u'HudCache', u'Players', u'RawHands', u'RawTourneys', u'Settings', u'Sites', u'TourneyTypes', u'Tourneys', u'TourneysPlayers'):
            self.query['get' + table] = u"SELECT * FROM " + table
        
        ################################
        # placeholders and substitution stuff
        ################################
        self.query['placeholder'] = u'?'


        # If using sqlite, use the ? placeholder instead of %s
        for k, q in list(self.query.items()):
            self.query[k] = re.sub('%s', '?', q)

if __name__ == "__main__":
#    just print the default queries and exit
    s = Sql()
    for key in s.query:
        print("For query " + key + ", sql =")
        print(s.query[key])
