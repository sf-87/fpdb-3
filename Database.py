from decimal import Decimal
import logging
import os
import sqlalchemy.pool as pool
import sys
from time import sleep

from Exceptions import FpdbError
import SQL

# logging has been set up in fpdb.py or HUD_main.py, use their settings:
log = logging.getLogger("db")

def adapt_decimal(d):
    return str(d)

# Keys used to index into player data in insert_hand_players.
HAND_PLAYERS_KEYS = [
    "startStack",
    "startBounty",
    "endBounty",
    "position",
    "seatNo",
    "card1",
    "card2",
    "startingHand",
    "winnings",
    "totalProfit",
    "street0VPIChance",
    "street0VPI",
    "street0AggrChance",
    "street0Aggr",
    "street0TBChance",
    "street0TBDone",
    "street0FBChance",
    "street0FBDone",
    "street0FoldTo3BChance",
    "street0FoldTo3BDone",
    "street0FoldTo4BChance",
    "street0FoldTo4BDone",
    "raiseToStealChance",
    "raiseToStealDone",
    "stealChance",
    "stealDone",
    "street1Seen",
    "street2Seen",
    "street3Seen",
    "sawShowdown",
    "otherRaisedStreet1",
    "otherRaisedStreet2",
    "otherRaisedStreet3",
    "foldToOtherRaisedStreet1",
    "foldToOtherRaisedStreet2",
    "foldToOtherRaisedStreet3",
    "wonWhenSeenStreet1",
    "foldBBToStealChance",
    "foldedBBToSteal",
    "foldSBToStealChance",
    "foldedSBToSteal",
    "street1CBChance",
    "street1CBDone",
    "street2CBChance",
    "street2CBDone",
    "street3CBChance",
    "street3CBDone",
    "foldToStreet1CBChance",
    "foldToStreet1CBDone",
    "foldToStreet2CBChance",
    "foldToStreet2CBDone",
    "foldToStreet3CBChance",
    "foldToStreet3CBDone",
    "street1CheckRaiseChance",
    "street1CheckRaiseDone",
    "street2CheckRaiseChance",
    "street2CheckRaiseDone",
    "street3CheckRaiseChance",
    "street3CheckRaiseDone"
]

CACHE_KEYS = [
    "n",
    "street0VPIChance",
    "street0VPI",
    "street0AggrChance",
    "street0Aggr",
    "street0TBChance",
    "street0TBDone",
    "street0FBChance",
    "street0FBDone",
    "street0FoldTo3BChance",
    "street0FoldTo3BDone",
    "street0FoldTo4BChance",
    "street0FoldTo4BDone",
    "raiseToStealChance",
    "raiseToStealDone",
    "stealChance",
    "stealDone",
    "street1Seen",
    "street2Seen",
    "street3Seen",
    "sawShowdown",
    "otherRaisedStreet1",
    "otherRaisedStreet2",
    "otherRaisedStreet3",
    "foldToOtherRaisedStreet1",
    "foldToOtherRaisedStreet2",
    "foldToOtherRaisedStreet3",
    "wonWhenSeenStreet1",
    "foldBBToStealChance",
    "foldedBBToSteal",
    "foldSBToStealChance",
    "foldedSBToSteal",
    "street1CBChance",
    "street1CBDone",
    "street2CBChance",
    "street2CBDone",
    "street3CBChance",
    "street3CBDone",
    "foldToStreet1CBChance",
    "foldToStreet1CBDone",
    "foldToStreet2CBChance",
    "foldToStreet2CBDone",
    "foldToStreet3CBChance",
    "foldToStreet3CBDone",
    "street1CheckRaiseChance",
    "street1CheckRaiseDone",
    "street2CheckRaiseChance",
    "street2CheckRaiseDone",
    "street3CheckRaiseChance",
    "street3CheckRaiseDone"
]

class Database(object):
    def __init__(self, config):
        self.database = config.database
        self.db_path = config.db_path
        self.hero_name = config.site.screen_name
        self.day_start = config.general.day_start
        self.session_timeout = config.imp.session_timeout
        self.sql = SQL.Sql()
        self.connection = None
        self.is_connected = False
        self.cursor = None
        self.gt_cache = {}  # GameTypeId cache
        self.t_cache = {}  # TourneyId cache
        self.p_cache = {}  # PlayerId cache
        self.tt_cache = {} # TourneyTypeId cache

        # Connect to db
        self.connect()

    def connect(self):
        import sqlite3
        sqlite3 = pool.manage(sqlite3, pool_size=1)

        log.info(f"Connecting to SQLite: {self.db_path}")

        if os.path.exists(self.db_path):
            self.connection = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            self.is_connected = True
            sqlite3.register_adapter(Decimal, adapt_decimal)
            self.cursor = self.connection.cursor()
            self.cursor.execute("PRAGMA temp_store=2")  # use memory for temp tables/indexes
            self.cursor.execute("PRAGMA journal_mode=WAL")  # use memory for temp tables/indexes
            self.cursor.execute("PRAGMA synchronous=0")  # don't wait for file writes to finish
            log.info(f"Connected to SQLite: {self.db_path}")
        else:
            raise FpdbError(f"SQLite database {self.database} does not exists")

    def commit(self):
        # sqlite commits can fail because of shared locks on the database (SQLITE_BUSY)
        # re-try commit if it fails in case this happened
        max_times = 5
        pause = 1
        ok = False

        for i in range(max_times):
            try:
                self.connection.commit()
                ok = True
            except Exception as e:
                log.info(f"Commit {i} failed: info={sys.exc_info()} value={e}")
                sleep(pause)

            if ok:
                break

        if not ok:
            log.error("Commit failed")
            raise FpdbError("SQLite commit failed")

    def disconnect(self):
        self.cursor.close()
        self.connection.close()
        self.is_connected = False

    def get_table_info(self, hand_id):
        self.cursor.execute(self.sql.query["getTableInfo"], [hand_id])
        return list(self.cursor.fetchone())

    def get_hand_count(self):
        self.cursor.execute(self.sql.query["getHandsCount"])
        return self.cursor.fetchone()[0]

    def get_tourney_count(self):
        self.cursor.execute(self.sql.query["getTourneysCount"])
        return self.cursor.fetchone()[0]

    def get_tourney_type_count(self):
        self.cursor.execute(self.sql.query["getTourneyTypesCount"])
        return self.cursor.fetchone()[0]

    def get_stats_from_hand(self, hand_id, hud_params, num_seats, table_type):
        if table_type == "tour":
            agg_bb_mult = hud_params.tour_agg_bb_mult
            seats_style = hud_params.tour_seats_style
        else:
            agg_bb_mult = hud_params.cash_agg_bb_mult
            seats_style = hud_params.cash_seats_style

        stat_dict = {}

        if seats_style == "A":
            seats_min, seats_max = 0, 9
        elif seats_style == "E":
            seats_min, seats_max = num_seats, num_seats
        else:
            seats_min, seats_max = 0, 9
            log.warning(f"Bad seats_style value: {seats_style}")

        data = [
            hand_id,
            agg_bb_mult,
            agg_bb_mult,
            seats_min,
            seats_max
        ]

        # Now get the stats
        self.cursor.execute(self.sql.query["getHudStats"], data)

        col_names = [desc[0] for desc in self.cursor.description]

        for row in self.cursor.fetchall():
            t_dict = {}

            for name, val in zip(col_names, row):
                t_dict[name] = val

            stat_dict[t_dict["player_id"]] = t_dict

        return stat_dict

    def reset_cache(self):
        self.gt_cache = {}
        self.t_cache = {}
        self.p_cache = {}
        self.tt_cache = {}

    def get_last_insert_id(self):
        return self.cursor.lastrowid

    def recreate_tables(self):
        self.drop_tables()
        self.reset_cache()
        self.create_tables()

        log.info("Finished recreating tables")

    def create_tables(self):
        log.debug("Creating tables")

        self.cursor.execute(self.sql.query["createFilesTable"])
        self.cursor.execute(self.sql.query["createGameTypesTable"])
        self.cursor.execute(self.sql.query["createPlayersTable"])
        self.cursor.execute(self.sql.query["createTourneyTypesTable"])
        self.cursor.execute(self.sql.query["createTourneysTable"])
        self.cursor.execute(self.sql.query["createHandsTable"])
        self.cursor.execute(self.sql.query["createHandPlayersTable"])
        self.cursor.execute(self.sql.query["createHandActionsTable"])
        self.cursor.execute(self.sql.query["createHudCacheTable"])

        log.debug("Creating unique indexes")

        self.cursor.execute(self.sql.query["createFilesIndex"])
        self.cursor.execute(self.sql.query["createPlayersIndex"])
        self.cursor.execute(self.sql.query["createTourneysIndex"])
        self.cursor.execute(self.sql.query["createHandsIndex"])
        self.cursor.execute(self.sql.query["createHandPlayersIndex"])
        self.cursor.execute(self.sql.query["createHudCacheIndex"])

        self.commit()

    def drop_tables(self):
        self.cursor.execute(self.sql.query["listTables"])

        for table in self.cursor.fetchall():
            log.info(f"{self.sql.query['dropTable']}'{table[0]}'")

            self.cursor.execute(f"{self.sql.query['dropTable']}{table[0]}")

        self.commit()
        self.cursor.execute("VACUUM") # clear space deleted

    def insert_hand(self, data):
        self.cursor.execute(self.sql.query["insertHand"], data)
        return self.get_last_insert_id()

    def insert_hand_player(self, data):
        self.cursor.execute(self.sql.query["insertHandPlayer"], data)
        return self.get_last_insert_id()

    def store_hand_players(self, hand_id, players_ids, hand_players):
        for player in hand_players:
            player_stats = hand_players.get(player)
            data = [hand_id, players_ids[player]]
            data += [player_stats[s] for s in HAND_PLAYERS_KEYS]
            self.insert_hand_player(data)

    def insert_hand_action(self, data):
        self.cursor.execute(self.sql.query["insertHandAction"], data)
        return self.get_last_insert_id()

    def store_hand_actions(self, hand_id, players_ids, hand_actions):
        for action in hand_actions:
            data = [
                    hand_id,
                    players_ids[hand_actions[action]["player"]],
                    hand_actions[action]["street"],
                    hand_actions[action]["action"],
                    hand_actions[action]["amount"],
                    hand_actions[action]["allIn"]
            ]
            self.insert_hand_action(data)

    def get_hud_cache_id(self, data):
        self.cursor.execute(self.sql.query["getHudCacheId"], data)
        result = self.cursor.fetchone()

        if not result:
            return 0

        return result[0]

    def insert_hud_cache(self, data):
        self.cursor.execute(self.sql.query["insertHudCache"], data)
        return self.get_last_insert_id()

    def update_hud_cache(self, data):
        self.cursor.execute(self.sql.query["updateHudCache"], data)

    def store_hud_cache(self, game_type_id, players_ids, hand_players):
        seats = len(players_ids)

        for player in hand_players:
            player_stats = hand_players.get(player)
            player_stats["n"] = 1
            k = [game_type_id, players_ids[player], seats]
            data = [player_stats[s] for s in CACHE_KEYS]

            cache_id = self.get_hud_cache_id(k)

            if cache_id == 0:
                self.insert_hud_cache(k + data)
            else:
                data += [cache_id]
                self.update_hud_cache(data)

    def get_file_id(self, file):
        self.cursor.execute(self.sql.query["getFileId"], [file])
        result = self.cursor.fetchone()

        if not result:
            return 0

        return result[0]

    def insert_file(self, data):
        self.cursor.execute(self.sql.query["insertFile"], data)
        return self.get_last_insert_id()

    def update_file(self, data):
        self.cursor.execute(self.sql.query["updateFile"], data)

    def get_hero_id(self):
        self.cursor.execute(self.sql.query["getPlayerId"], [self.hero_name])
        return self.cursor.fetchone()[0]

    def is_hand_duplicate(self, hand_no):
        self.cursor.execute(self.sql.query["getHandId"], [hand_no])
        result = self.cursor.fetchone()

        if not result:
            return False

        return True

    def get_players_ids(self, players, hero):
        result = {}

        for player in players:
            if len(self.p_cache) == 0 or player not in self.p_cache:
                self.p_cache[player] = self.insert_player(player, player == hero)

            result[player] = self.p_cache[player]

        return result

    def insert_player(self, name, hero):
        self.cursor.execute(self.sql.query["getPlayerId"], [name])
        result = self.cursor.fetchone()

        if not result:
            self.cursor.execute(self.sql.query["insertPlayer"], [name, hero])
            return self.get_last_insert_id()

        return result[0]

    def get_game_type_id(self, game):
        data = (
            game["type"],
            game["currency"],
            Decimal(game["sb"]),
            Decimal(game["bb"]),
            game["maxSeats"],
            int(game["ante"])
        )

        if len(self.gt_cache) == 0 or data not in self.gt_cache:
            self.gt_cache[data] = self.insert_game_type(data)

        return self.gt_cache[data]

    def insert_game_type(self, data):
        self.cursor.execute(self.sql.query["getGameTypeId"], data)
        result = self.cursor.fetchone()

        if not result:
            self.cursor.execute(self.sql.query["insertGameType"], data)
            return self.get_last_insert_id()

        return result[0]

    def get_tourney_type_id(self, hand):
        data = (
            hand.buy_in_currency,
            hand.buy_in,
            hand.fee,
            hand.game_type["maxSeats"],
            hand.is_ko,
            hand.ko_bounty,
            hand.speed,
            hand.is_private,
            hand.is_sng
        )

        if len(self.tt_cache) == 0 or data not in self.tt_cache:
            self.tt_cache[data] = self.insert_tourney_type(hand.tour_no, data)

        return self.tt_cache[data]

    def insert_tourney_type(self, tour_no, data):
        self.cursor.execute(self.sql.query["getTourneyTypeIdFromTourney"], [tour_no])
        result = self.cursor.fetchone()

        if not result:
            self.cursor.execute(self.sql.query["getTourneyTypeId"], data)
            result = self.cursor.fetchone()

            if not result:
                self.cursor.execute(self.sql.query["insertTourneyType"], data)
                return self.get_last_insert_id()

        return result[0]

    def get_tourney_id(self, tour_no):
        self.cursor.execute(self.sql.query["getTourneyId"], [tour_no])
        result = self.cursor.fetchone()

        if not result:
            return 0

        return result[0]

    def get_tourney_id_from_hand(self, hand):
        data = [hand.tourney_type_id, hand.tour_no, None, None, hand.start_time, None, None, 0]

        if len(self.t_cache) == 0 or hand.tour_no not in self.t_cache:
            self.t_cache[hand.tour_no] = self.insert_tourney(data)

        return self.t_cache[hand.tour_no]

    def insert_tourney(self, data):
        result = self.get_tourney_id(data[1])

        if result == 0:
            self.cursor.execute(self.sql.query["insertTourney"], data)
            return self.get_last_insert_id()

        return result

    def update_tourney(self, data):
        self.cursor.execute(self.sql.query["updateTourney"], data)

    def update_tourney_bounties(self, data):
        self.cursor.execute(self.sql.query["updateTourneyBounties"], data)

    def get_tourney_player_detailed_stats(self, start_date, end_date):
        self.cursor.execute(self.sql.query["getTourneyDetailedStats"], [start_date, end_date])
        return self.cursor.fetchall()

    def get_buy_ins(self):
        self.cursor.execute(self.sql.query["getBuyIns"])
        return self.cursor.fetchall()

    def get_tourney_player_graph_stats(self, start_date, end_date, tourney_buy_ins):
        q = self.sql.query["getTourneyGraphStats"]
        q = q.replace("<tourneyBuyIns>", tourney_buy_ins if tourney_buy_ins != "" else "1 = 0")
        self.cursor.execute(q, [start_date, end_date])
        return self.cursor.fetchall()

    def get_cash_player_detailed_stats(self, start_date, end_date, stakes):
        q = self.sql.query["getCashDetailedStats"]
        q = q.replace("<stakes>", stakes if stakes != "" else "1 = 0")
        self.cursor.execute(q, [start_date, end_date, self.get_hero_id()])
        return self.cursor.fetchall()

    def get_cash_hands_player_detailed_stats(self, start_date, end_date, stakes):
        q = self.sql.query["getCashHandsDetailedStats"]
        q = q.replace("<stakes>", stakes if stakes != "" else "1 = 0")
        self.cursor.execute(q, [start_date, end_date, self.get_hero_id()])
        return self.cursor.fetchall()

    def get_stakes(self):
        self.cursor.execute(self.sql.query["getStakes"])
        return self.cursor.fetchall()

    def get_cash_player_graph_stats(self, start_date, end_date, stakes):
        q = self.sql.query["getCashGraphStats"]
        q = q.replace("<stakes>", stakes if stakes != "" else "1 = 0")
        self.cursor.execute(q, [start_date, end_date, self.get_hero_id()])
        return self.cursor.fetchall()

    def get_cash_player_sessions_stats(self, start_date, end_date, stakes):
        q = self.sql.query["getCashSessionStats"]
        q = q.replace("<stakes>", stakes if stakes != "" else "1 = 0")
        self.cursor.execute(q, [start_date, end_date, self.get_hero_id()])
        return self.cursor.fetchall()
