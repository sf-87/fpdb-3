class Sql(object):
    def __init__(self):
        self.query = {}

        ####################################
        # Database management
        ####################################

        self.query["listTables"] = "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        self.query["dropTable"] = "DROP TABLE IF EXISTS "

        ####################################
        # Create Files
        ####################################

        self.query["createFilesTable"] = """CREATE TABLE Files (
                    id INTEGER PRIMARY KEY NOT NULL,
                    file TEXT NOT NULL,
                    startTime TEXT NOT NULL,
                    endTime TEXT,
                    hands INTEGER,
                    stored INTEGER,
                    duplicates INTEGER,
                    errors INTEGER,
                    finished INTEGER)"""

        ####################################
        # Create GameTypes
        ####################################

        self.query["createGameTypesTable"] = """CREATE TABLE GameTypes (
                    id INTEGER PRIMARY KEY NOT NULL,
                    smallBlind INTEGER NOT NULL,
                    bigBlind INTEGER NOT NULL,
                    maxSeats INTEGER NOT NULL,
                    ante INTEGER NOT NULL)"""

        ####################################
        # Create Players
        ####################################

        self.query["createPlayersTable"] = """CREATE TABLE Players (
                    id INTEGER PRIMARY KEY NOT NULL,
                    name TEXT NOT NULL,
                    hero INTEGER NOT NULL)"""

        ####################################
        # Create TourneyTypes
        ####################################

        self.query["createTourneyTypesTable"] = """CREATE TABLE TourneyTypes (
                    id INTEGER PRIMARY KEY NOT NULL,
                    currency TEXT NOT NULL,
                    buyIn REAL NOT NULL,
                    fee REAL NOT NULL,
                    maxSeats INTEGER NOT NULL,
                    knockout INTEGER NOT NULL,
                    koBounty REAL,
                    speed TEXT NOT NULL,
                    private INTEGER NOT NULL,
                    sng INTEGER NOT NULL)"""

        ####################################
        # Create Tourneys
        ####################################

        self.query["createTourneysTable"] = """CREATE TABLE Tourneys (
                    id INTEGER PRIMARY KEY NOT NULL,
                    tourneyTypeId INTEGER NOT NULL,
                    tourneyNo INTEGER NOT NULL,
                    entries INTEGER,
                    prizePool REAL,
                    startTime TEXT NOT NULL,
                    rank INTEGER,
                    winnings REAL,
                    bounties REAL NOT NULL,
                    FOREIGN KEY (tourneyTypeId) REFERENCES TourneyTypes (id))"""

        ####################################
        # Create Hands
        ####################################

        self.query["createHandsTable"] = """CREATE TABLE Hands (
                    id INTEGER PRIMARY KEY NOT NULL,
                    tableName TEXT NOT NULL,
                    handNo INTEGER NOT NULL,
                    tourneyId INTEGER NOT NULL,
                    gameTypeId INTEGER NOT NULL,
                    fileId INTEGER NOT NULL,
                    startTime TEXT NOT NULL,
                    seats INTEGER NOT NULL,
                    heroSeat INTEGER NOT NULL,
                    boardCard1 TEXT,
                    boardCard2 TEXT,
                    boardCard3 TEXT,
                    boardCard4 TEXT,
                    boardCard5 TEXT,
                    playersVPI INTEGER NOT NULL,
                    FOREIGN KEY (tourneyId) REFERENCES Tourneys (id),
                    FOREIGN KEY (gameTypeId) REFERENCES GameTypes (id),
                    FOREIGN KEY (fileId) REFERENCES Files (id))"""

        ####################################
        # Create HandPlayers
        ####################################

        self.query["createHandPlayersTable"] = """CREATE TABLE HandPlayers (
                    id INTEGER PRIMARY KEY NOT NULL,
                    handId INTEGER NOT NULL,
                    playerId INTEGER NOT NULL,
                    startStack INTEGER NOT NULL,
                    startBounty REAL,
                    endBounty REAL,
                    position TEXT NOT NULL,
                    seatNo INTEGER NOT NULL,
                    card1 TEXT,
                    card2 TEXT,
                    street0VPIChance INTEGER NOT NULL,
                    street0VPI INTEGER NOT NULL,
                    street0AggrChance INTEGER NOT NULL,
                    street0Aggr INTEGER NOT NULL,
                    street0TBChance INTEGER NOT NULL,
                    street0TBDone INTEGER NOT NULL,
                    street0FBChance INTEGER NOT NULL,
                    street0FBDone INTEGER NOT NULL,
                    street0FoldTo3BChance INTEGER NOT NULL,
                    street0FoldTo3BDone INTEGER NOT NULL,
                    street0FoldTo4BChance INTEGER NOT NULL,
                    street0FoldTo4BDone INTEGER NOT NULL,
                    raiseToStealChance INTEGER NOT NULL,
                    raiseToStealDone INTEGER NOT NULL,
                    stealChance INTEGER NOT NULL,
                    stealDone INTEGER NOT NULL,
                    otherRaisedStreet1 INTEGER NOT NULL,
                    otherRaisedStreet2 INTEGER NOT NULL,
                    otherRaisedStreet3 INTEGER NOT NULL,
                    foldToOtherRaisedStreet1 INTEGER NOT NULL,
                    foldToOtherRaisedStreet2 INTEGER NOT NULL,
                    foldToOtherRaisedStreet3 INTEGER NOT NULL,
                    foldBBToStealChance INTEGER NOT NULL,
                    foldedBBToSteal INTEGER NOT NULL,
                    foldSBToStealChance INTEGER NOT NULL,
                    foldedSBToSteal INTEGER NOT NULL,
                    street1CBChance INTEGER NOT NULL,
                    street1CBDone INTEGER NOT NULL,
                    street2CBChance INTEGER NOT NULL,
                    street2CBDone INTEGER NOT NULL,
                    street3CBChance INTEGER NOT NULL,
                    street3CBDone INTEGER NOT NULL,
                    foldToStreet1CBChance INTEGER NOT NULL,
                    foldToStreet1CBDone INTEGER NOT NULL,
                    foldToStreet2CBChance INTEGER NOT NULL,
                    foldToStreet2CBDone INTEGER NOT NULL,
                    foldToStreet3CBChance INTEGER NOT NULL,
                    foldToStreet3CBDone INTEGER NOT NULL,
                    street1CheckRaiseChance INTEGER NOT NULL,
                    street1CheckRaiseDone INTEGER NOT NULL,
                    street2CheckRaiseChance INTEGER NOT NULL,
                    street2CheckRaiseDone INTEGER NOT NULL,
                    street3CheckRaiseChance INTEGER NOT NULL,
                    street3CheckRaiseDone INTEGER NOT NULL,
                    FOREIGN KEY (handId) REFERENCES Hands (id),
                    FOREIGN KEY (playerId) REFERENCES Players (id))"""

        ####################################
        # Create HandActions
        ####################################

        self.query["createHandActionsTable"] = """CREATE TABLE HandActions (
                    id INTEGER PRIMARY KEY NOT NULL,
                    handId INTEGER NOT NULL,
                    playerId INTEGER NOT NULL,
                    street TEXT NOT NULL,
                    action TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    allIn INTEGER NOT NULL,
                    FOREIGN KEY (handId) REFERENCES Hands (id),
                    FOREIGN KEY (playerId) REFERENCES Players (id))"""

        ####################################
        # Create HudCache
        ####################################

        self.query["createHudCacheTable"] = """CREATE TABLE HudCache (
                    id INTEGER PRIMARY KEY NOT NULL,
                    gameTypeId INTEGER NOT NULL,
                    playerId INTEGER NOT NULL,
                    seats INTEGER NOT NULL,
                    n INTEGER NOT NULL,
                    street0VPIChance INTEGER NOT NULL,
                    street0VPI INTEGER NOT NULL,
                    street0AggrChance INTEGER NOT NULL,
                    street0Aggr INTEGER NOT NULL,
                    street0TBChance INTEGER NOT NULL,
                    street0TBDone INTEGER NOT NULL,
                    street0FBChance INTEGER NOT NULL,
                    street0FBDone INTEGER NOT NULL,
                    street0FoldTo3BChance INTEGER NOT NULL,
                    street0FoldTo3BDone INTEGER NOT NULL,
                    street0FoldTo4BChance INTEGER NOT NULL,
                    street0FoldTo4BDone INTEGER NOT NULL,
                    raiseToStealChance INTEGER NOT NULL,
                    raiseToStealDone INTEGER NOT NULL,
                    stealChance INTEGER NOT NULL,
                    stealDone INTEGER NOT NULL,
                    otherRaisedStreet1 INTEGER NOT NULL,
                    otherRaisedStreet2 INTEGER NOT NULL,
                    otherRaisedStreet3 INTEGER NOT NULL,
                    foldToOtherRaisedStreet1 INTEGER NOT NULL,
                    foldToOtherRaisedStreet2 INTEGER NOT NULL,
                    foldToOtherRaisedStreet3 INTEGER NOT NULL,
                    foldBBToStealChance INTEGER NOT NULL,
                    foldedBBToSteal INTEGER NOT NULL,
                    foldSBToStealChance INTEGER NOT NULL,
                    foldedSBToSteal INTEGER NOT NULL,
                    street1CBChance INTEGER NOT NULL,
                    street1CBDone INTEGER NOT NULL,
                    street2CBChance INTEGER NOT NULL,
                    street2CBDone INTEGER NOT NULL,
                    street3CBChance INTEGER NOT NULL,
                    street3CBDone INTEGER NOT NULL,
                    foldToStreet1CBChance INTEGER NOT NULL,
                    foldToStreet1CBDone INTEGER NOT NULL,
                    foldToStreet2CBChance INTEGER NOT NULL,
                    foldToStreet2CBDone INTEGER NOT NULL,
                    foldToStreet3CBChance INTEGER NOT NULL,
                    foldToStreet3CBDone INTEGER NOT NULL,
                    street1CheckRaiseChance INTEGER NOT NULL,
                    street1CheckRaiseDone INTEGER NOT NULL,
                    street2CheckRaiseChance INTEGER NOT NULL,
                    street2CheckRaiseDone INTEGER NOT NULL,
                    street3CheckRaiseChance INTEGER NOT NULL,
                    street3CheckRaiseDone INTEGER NOT NULL,
                    FOREIGN KEY (gameTypeId) REFERENCES GameTypes (id),
                    FOREIGN KEY (playerId) REFERENCES Players (id))"""

        ####################################
        # Create Indexes
        ####################################

        self.query["createFilesIndex"] = "CREATE UNIQUE INDEX UK_Files ON Files (file)"
        self.query["createPlayersIndex"] = "CREATE UNIQUE INDEX UK_Players ON Players (name)"
        self.query["createTourneysIndex"] = "CREATE UNIQUE INDEX UK_Tourneys ON Tourneys (tourneyNo)"
        self.query["createHandsIndex"] = "CREATE UNIQUE INDEX UK_Hands ON Hands (handNo)"
        self.query["createHandPlayersIndex"] = "CREATE UNIQUE INDEX UK_HandPlayers ON HandPlayers (handId, playerId)"
        self.query["createHudCacheIndex"] = "CREATE UNIQUE INDEX UK_HudCache ON HudCache (gameTypeId, playerId, seats)"

        ####################################
        # Counts for DB stats window
        ####################################

        self.query["getHandsCount"] = "SELECT COUNT(*) FROM Hands"
        self.query["getTourneysCount"] = "SELECT COUNT(*) FROM Tourneys"
        self.query["getTourneyTypesCount"] = "SELECT COUNT(*) FROM TourneyTypes"

        ####################################
        # Select basic info
        ####################################

        self.query["getBuyIns"] = "SELECT DISTINCT buyIn, fee FROM TourneyTypes ORDER BY buyIn, fee"

        ####################################
        # Queries for Files table
        ####################################

        self.query["getFileId"] = "SELECT id FROM Files WHERE file = ?"

        self.query["insertFile"] = """INSERT INTO Files (file, startTime, hands, stored, duplicates, errors, finished)
                                      VALUES (?, ?, ?, ?, ?, ?, ?)"""

        self.query["updateFile"] = """UPDATE Files
                                      SET endTime = ?,
                                          hands = hands + ?,
                                          stored = stored + ?,
                                          duplicates = duplicates + ?,
                                          errors = errors + ?,
                                          finished = ?
                                      WHERE id = ?"""

        ####################################
        # Queries for GameTypes table
        ####################################

        self.query["getGameTypeId"] = "SELECT id FROM GameTypes WHERE smallBlind = ? AND bigBlind = ? AND maxSeats = ? AND ante = ?"

        self.query["insertGameType"] = "INSERT INTO GameTypes (smallBlind, bigBlind, maxSeats, ante) VALUES (?, ?, ?, ?)"

        self.query["getGameType"] = """SELECT gt.*
                                       FROM Hands h
                                       INNER JOIN GameTypes gt
                                       ON gt.id = h.gameTypeId
                                       WHERE h.id = ?"""

        ####################################
        # Queries for Players table
        ####################################

        self.query["getPlayerId"] = "SELECT id FROM Players WHERE name = ?"

        self.query["insertPlayer"] = "INSERT INTO Players (name, hero) VALUES (?, ?)"

        ####################################
        # Queries for TourneyTypes table
        ####################################

        self.query["getTourneyTypeId"] = """SELECT id
                                            FROM TourneyTypes
                                            WHERE currency = ?
                                            AND buyIn = ?
                                            AND fee = ?
                                            AND maxSeats = ?
                                            AND knockout = ?
                                            AND koBounty = ?
                                            AND speed = ?
                                            AND private = ?
                                            AND sng = ?"""

        self.query["insertTourneyType"] = """INSERT INTO TourneyTypes (currency, buyIn, fee, maxSeats, knockout, koBounty, speed, private, sng)
                                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""

        ####################################
        # Queries for Tourneys table
        ####################################

        self.query["getTourneyTypeIdFromTourney"] = "SELECT tourneyTypeId FROM Tourneys WHERE tourneyNo = ?"

        self.query["getTourneyId"] = "SELECT id FROM Tourneys WHERE tourneyNo = ?"

        self.query["insertTourney"] = """INSERT INTO Tourneys (tourneyTypeId, tourneyNo, entries, prizePool, startTime, rank, winnings, bounties)
                                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""

        self.query["updateTourney"] = "UPDATE Tourneys SET entries = ?, prizePool = ?, startTime = ?, rank = ?, winnings = ? WHERE id = ?"

        self.query["updateTourneyBounties"] = "UPDATE Tourneys SET bounties = bounties + ? WHERE id = ?"

        ####################################
        # Queries for Hands table
        ####################################

        self.query["getHandId"] = "SELECT id FROM Hands WHERE handNo = ?"

        self.query["insertHand"] = """INSERT INTO Hands (tableName, handNo, tourneyId, gameTypeId, fileId, startTime,
                                                         seats, heroSeat, boardCard1, boardCard2, boardCard3, boardCard4,
                                                         boardCard5, playersVPI)
                                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

        self.query["getTableInfo"] = """SELECT t.tourneyNo,
                                               h.tableName,
                                               gt.maxSeats,
                                               COUNT(*)
                                        FROM Hands h
                                        INNER JOIN GameTypes gt
                                        ON gt.id = h.gameTypeId
                                        INNER JOIN HandPlayers hp
                                        ON hp.handId = h.id
                                        INNER JOIN Tourneys t
                                        ON t.id = h.tourneyId
                                        WHERE h.id = ?
                                        GROUP BY h.tableName,
                                                 gt.maxSeats"""

        ####################################
        # Queries for HandPlayers table
        ####################################

        self.query["insertHandPlayer"] = """INSERT INTO HandPlayers (handId, playerId, startStack, startBounty, endBounty, position,
                                                                     seatNo, card1, card2, street0VPIChance, street0VPI, street0AggrChance,
                                                                     street0Aggr, street0TBChance, street0TBDone, street0FBChance, street0FBDone, street0FoldTo3BChance,
                                                                     street0FoldTo3BDone, street0FoldTo4BChance, street0FoldTo4BDone, raiseToStealChance, raiseToStealDone, stealChance,
                                                                     stealDone, otherRaisedStreet1, otherRaisedStreet2, otherRaisedStreet3, foldToOtherRaisedStreet1, foldToOtherRaisedStreet2,
                                                                     foldToOtherRaisedStreet3, foldBBToStealChance, foldedBBToSteal, foldSBToStealChance, foldedSBToSteal, street1CBChance,
                                                                     street1CBDone, street2CBChance, street2CBDone, street3CBChance, street3CBDone, foldToStreet1CBChance,
                                                                     foldToStreet1CBDone, foldToStreet2CBChance, foldToStreet2CBDone, foldToStreet3CBChance, foldToStreet3CBDone, street1CheckRaiseChance,
                                                                     street1CheckRaiseDone, street2CheckRaiseChance, street2CheckRaiseDone, street3CheckRaiseChance, street3CheckRaiseDone)
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                                                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

        ####################################
        # Queries for HandActions table
        ####################################

        self.query["insertHandAction"] = """INSERT INTO HandActions (handId, playerId, street, action, amount, allIn)
                                            VALUES (?, ?, ?, ?, ?, ?)"""

        ####################################
        # Queries for HudCache table
        ####################################

        self.query["getHudCacheId"] = """SELECT id
                                         FROM HudCache
                                         WHERE gameTypeId = ?
                                         AND playerId = ?
                                         AND seats = ?"""

        self.query["insertHudCache"] = """INSERT INTO HudCache (gameTypeId, playerId, seats, n, street0VPIChance, street0VPI,
                                                                street0AggrChance, street0Aggr, street0TBChance, street0TBDone, street0FBChance, street0FBDone,
                                                                street0FoldTo3BChance, street0FoldTo3BDone, street0FoldTo4BChance, street0FoldTo4BDone, raiseToStealChance, raiseToStealDone,
                                                                stealChance, stealDone, otherRaisedStreet1, otherRaisedStreet2, otherRaisedStreet3, foldToOtherRaisedStreet1,
                                                                foldToOtherRaisedStreet2, foldToOtherRaisedStreet3, foldBBToStealChance, foldedBBToSteal, foldSBToStealChance, foldedSBToSteal,
                                                                street1CBChance, street1CBDone, street2CBChance, street2CBDone, street3CBChance, street3CBDone,
                                                                foldToStreet1CBChance, foldToStreet1CBDone, foldToStreet2CBChance, foldToStreet2CBDone, foldToStreet3CBChance, foldToStreet3CBDone,
                                                                street1CheckRaiseChance, street1CheckRaiseDone, street2CheckRaiseChance, street2CheckRaiseDone, street3CheckRaiseChance, street3CheckRaiseDone)
                                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                                                  ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

        self.query["updateHudCache"] = """UPDATE HudCache
                                          SET n = n + ?,
                                              street0VPIChance = street0VPIChance + ?,
                                              street0VPI = street0VPI + ?,
                                              street0AggrChance = street0AggrChance + ?,
                                              street0Aggr = street0Aggr + ?,
                                              street0TBChance = street0TBChance + ?,
                                              street0TBDone = street0TBDone + ?,
                                              street0FBChance = street0FBChance + ?,
                                              street0FBDone = street0FBDone + ?,
                                              street0FoldTo3BChance = street0FoldTo3BChance + ?,
                                              street0FoldTo3BDone = street0FoldTo3BDone + ?,
                                              street0FoldTo4BChance = street0FoldTo4BChance + ?,
                                              street0FoldTo4BDone = street0FoldTo4BDone + ?,
                                              raiseToStealChance = raiseToStealChance + ?,
                                              raiseToStealDone = raiseToStealDone + ?,
                                              stealChance = stealChance + ?,
                                              stealDone = stealDone + ?,
                                              otherRaisedStreet1 = otherRaisedStreet1 + ?,
                                              otherRaisedStreet2 = otherRaisedStreet2 + ?,
                                              otherRaisedStreet3 = otherRaisedStreet3 + ?,
                                              foldToOtherRaisedStreet1 = foldToOtherRaisedStreet1 + ?,
                                              foldToOtherRaisedStreet2 = foldToOtherRaisedStreet2 + ?,
                                              foldToOtherRaisedStreet3 = foldToOtherRaisedStreet3 + ?,
                                              foldBBToStealChance = foldBBToStealChance + ?,
                                              foldedBBToSteal = foldedBBToSteal + ?,
                                              foldSBToStealChance = foldSBToStealChance + ?,
                                              foldedSBToSteal = foldedSBToSteal + ?,
                                              street1CBChance = street1CBChance + ?,
                                              street1CBDone = street1CBDone + ?,
                                              street2CBChance = street2CBChance + ?,
                                              street2CBDone = street2CBDone + ?,
                                              street3CBChance = street3CBChance + ?,
                                              street3CBDone = street3CBDone + ?,
                                              foldToStreet1CBChance = foldToStreet1CBChance + ?,
                                              foldToStreet1CBDone = foldToStreet1CBDone + ?,
                                              foldToStreet2CBChance = foldToStreet2CBChance + ?,
                                              foldToStreet2CBDone = foldToStreet2CBDone + ?,
                                              foldToStreet3CBChance = foldToStreet3CBChance + ?,
                                              foldToStreet3CBDone = foldToStreet3CBDone + ?,
                                              street1CheckRaiseChance = street1CheckRaiseChance + ?,
                                              street1CheckRaiseDone = street1CheckRaiseDone + ?,
                                              street2CheckRaiseChance = street2CheckRaiseChance + ?,
                                              street2CheckRaiseDone = street2CheckRaiseDone + ?,
                                              street3CheckRaiseChance = street3CheckRaiseChance + ?,
                                              street3CheckRaiseDone = street3CheckRaiseDone + ?
                                          WHERE id = ?"""

        self.query["getHudStats"] = """SELECT hc.playerId                       AS player_id,
                                              p.name                            AS screen_name,
                                              hp.seatNo                         AS seat,
                                              SUM(hc.n)                         AS n,
                                              SUM(hc.street0VPIChance)          AS vpip_opp,
                                              SUM(hc.street0VPI)                AS vpip,
                                              SUM(hc.street0AggrChance)         AS pfr_opp,
                                              SUM(hc.street0Aggr)               AS pfr,
                                              SUM(hc.street0TBChance)           AS tb_opp_0,
                                              SUM(hc.street0TBDone)             AS tb_0,
                                              SUM(hc.street0FBChance)           AS fb_opp_0,
                                              SUM(hc.street0FBDone)             AS fb_0,
                                              SUM(hc.street0FoldTo3BChance)     AS f3b_opp_0,
                                              SUM(hc.street0FoldTo3BDone)       AS f3b_0,
                                              SUM(hc.street0FoldTo4BChance)     AS f4b_opp_0,
                                              SUM(hc.street0FoldTo4BDone)       AS f4b_0,
                                              SUM(hc.raiseToStealChance)        AS rts_opp,
                                              SUM(hc.raiseToStealDone)          AS rts,
                                              SUM(hc.otherRaisedStreet1)        AS was_raised_1,
                                              SUM(hc.otherRaisedStreet2)        AS was_raised_2,
                                              SUM(hc.otherRaisedStreet3)        AS was_raised_3,
                                              SUM(hc.foldToOtherRaisedStreet1)  AS f_freq_1,
                                              SUM(hc.foldToOtherRaisedStreet2)  AS f_freq_2,
                                              SUM(hc.foldToOtherRaisedStreet3)  AS f_freq_3,
                                              SUM(hc.stealChance)               AS steal_opp,
                                              SUM(hc.stealDone)                 AS steal,
                                              SUM(hc.foldSBToStealChance)       AS sb_stolen,
                                              SUM(hc.foldedSBToSteal)           AS sb_not_def,
                                              SUM(hc.foldBBToStealChance)       AS bb_stolen,
                                              SUM(hc.foldedBBToSteal)           AS bb_not_def,
                                              SUM(hc.street1CBChance)           AS cb_opp_1,
                                              SUM(hc.street1CBDone)             AS cb_1,
                                              SUM(hc.street2CBChance)           AS cb_opp_2,
                                              SUM(hc.street2CBDone)             AS cb_2,
                                              SUM(hc.street3CBChance)           AS cb_opp_3,
                                              SUM(hc.street3CBDone)             AS cb_3,
                                              SUM(hc.foldToStreet1CBChance)     AS f_cb_opp_1,
                                              SUM(hc.foldToStreet1CBDone)       AS f_cb_1,
                                              SUM(hc.foldToStreet2CBChance)     AS f_cb_opp_2,
                                              SUM(hc.foldToStreet2CBDone)       AS f_cb_2,
                                              SUM(hc.foldToStreet3CBChance)     AS f_cb_opp_3,
                                              SUM(hc.foldToStreet3CBDone)       AS f_cb_3,
                                              SUM(hc.street1CheckRaiseChance)   AS cr_opp_1,
                                              SUM(hc.street1CheckRaiseDone)     AS cr_1,
                                              SUM(hc.street2CheckRaiseChance)   AS cr_opp_2,
                                              SUM(hc.street2CheckRaiseDone)     AS cr_2,
                                              SUM(hc.street3CheckRaiseChance)   AS cr_opp_3,
                                              SUM(hc.street3CheckRaiseDone)     AS cr_3
                                       FROM Hands h
                                       INNER JOIN HandPlayers hp
                                       ON hp.handId = h.id
                                       INNER JOIN HudCache hc
                                       ON hc.playerId = hp.playerId
                                       INNER JOIN Players p
                                       ON p.id = hc.playerId
                                       WHERE h.id = ?
                                       AND hc.gameTypeId IN (
                                                              SELECT gt2.id
                                                              FROM GameTypes gt1
                                                              INNER JOIN GameTypes gt2
                                                              ON gt2.bigBlind <= gt1.bigBlind * ?
                                                              AND gt2.bigBlind >= gt1.bigBlind / ?
                                                              WHERE gt1.id = ?
                                                            )
                                       AND hc.seats BETWEEN ? AND ?
                                       GROUP BY hc.playerId, p.name, hp.seatNo
                                       ORDER BY hc.playerId, p.name, hp.seatNo"""

        ####################################
        # Queries for Tourney Stats
        ####################################

        self.query["getTourneyDetailedStats"] = """SELECT printf("%.2f", tt.buyIn)                                                                          AS buyIn,
                                                          printf("%.2f", tt.fee)                                                                            AS fee,
                                                          printf("%d", tt.maxSeats)                                                                         AS maxSeats,
					                               	      IIF(tt.sng = 1, 'Yes', 'No')                                                                      AS sng,
					                               	      IIF(tt.knockout = 1, 'Yes', 'No')                                                                 AS knockout,
                                                          tt.speed                                                                                          AS speed,
                                                          printf("%d", COUNT(1))                                                                            AS tourneyCount,
                                                          printf("%.2f", (CAST(SUM(CASE WHEN t.winnings > 0 THEN 1 ELSE 0 END) AS REAL) / COUNT(1)) * 100)  AS itm,
                                                          printf("%d", SUM(CASE WHEN t.rank = 1 THEN 1 ELSE 0 END))                                         AS first,
                                                          printf("%d", SUM(CASE WHEN t.rank = 2 THEN 1 ELSE 0 END))                                         AS second,
                                                          printf("%d", SUM(CASE WHEN t.rank = 3 THEN 1 ELSE 0 END))                                         AS third,
                                                          printf("%d", SUM(CASE WHEN t.rank = 4 THEN 1 ELSE 0 END))                                         AS fourth,
                                                          printf("%d", SUM(CASE WHEN t.rank = 5 THEN 1 ELSE 0 END))                                         AS fifth,
                                                          printf("%d", SUM(CASE WHEN t.rank = 6 THEN 1 ELSE 0 END))                                         AS sixth,
                                                          printf("%d", SUM(CASE WHEN t.rank > 0 THEN 0 ELSE 1 END))                                         AS unknown,
                                                          printf("%.2f", SUM(tt.buyIn + tt.fee))                                                            AS spent,
                                                          printf("%.2f", SUM(t.winnings + t.bounties))                                                      AS won,
                                                          printf("%.2f", SUM(t.winnings + t.bounties - tt.buyIn - tt.fee))	 						        AS net,
														  printf("%.2f", (SUM(t.winnings + t.bounties - tt.buyIn - tt.fee) / SUM(tt.buyIn + tt.fee)) * 100) AS roi,
														  printf("%.2f", SUM(t.winnings + t.bounties - tt.buyIn - tt.fee) / COUNT(1))                       AS profitPerTourney
                                                   FROM Tourneys t
                                                   INNER JOIN TourneyTypes tt
                                                   ON tt.Id = t.tourneyTypeId
                                                   WHERE t.startTime > ?
                                                   AND t.startTime < ?
                                                   GROUP BY t.tourneyTypeId
                                                   ORDER BY tt.sng DESC, tt.buyIn, tt.fee, tt.maxSeats, tt.knockout"""

        self.query["getTourneyGraphStats"] = """SELECT t.winnings + t.bounties - tt.buyIn - tt.fee
                                                FROM Tourneys t
                                                INNER JOIN TourneyTypes tt
                                                ON tt.id = t.tourneyTypeId
                                                WHERE t.startTime > ?
                                                AND t.startTime < ?
                                                AND (<tourneyBuyIns>)
                                                ORDER BY t.startTime"""
