import os
import sqlite3
import threading

import log
lock = threading.Lock()


class DBHelper:
    __connection = None
    __instance = None
    __db_path = None

    def __init__(self):
        config_path = os.environ.get('NASTOOL_CONFIG')
        if not config_path:
            print("【RUN】NASTOOL_CONFIG 环境变量未设置，程序无法工作，正在退出...")
            quit()
        self.__db_path = os.path.join(os.path.dirname(config_path), 'user.db')
        self.__connection = sqlite3.connect(self.__db_path, check_same_thread=False)
        self.__init_tables()

    @staticmethod
    def get_instance():
        if DBHelper.__instance:
            return DBHelper.__instance
        try:
            lock.acquire()
            if not DBHelper.__instance:
                DBHelper.__instance = DBHelper()
        finally:
            lock.release()
        return DBHelper.__instance

    def __init_tables(self):
        cursor = self.__connection.cursor()
        try:
            # Jackett搜索结果表
            cursor.execute('''CREATE TABLE IF NOT EXISTS JACKETT_TORRENTS
                   (ID INTEGER PRIMARY KEY AUTOINCREMENT     NOT NULL,
                   TORRENT_NAME    TEXT,
                   ENCLOSURE    TEXT,
                   DESCRIPTION    TEXT,
                   TYPE TEXT,
                   TITLE    TEXT,
                   YEAR    TEXT,
                   SEASON    TEXT,
                   EPISODE    TEXT,
                   ES_STRING    TEXT,
                   VOTE    TEXT,
                   IMAGE    TEXT,
                   RES_TYPE    TEXT,
                   RES_ORDER    TEXT,
                   SIZE    INTEGER,
                   SEEDERS    INTEGER,
                   PEERS    INTEGER,                   
                   SITE    TEXT,
                   SITE_ORDER    TEXT);''')
            # RSS下载记录表
            cursor.execute('''CREATE TABLE IF NOT EXISTS RSS_TORRENTS
                                   (ID INTEGER PRIMARY KEY AUTOINCREMENT     NOT NULL,
                                   TORRENT_NAME    TEXT,
                                   ENCLOSURE    TEXT,
                                   TYPE TEXT,
                                   TITLE    TEXT,
                                   YEAR    TEXT,
                                   SEASON    TEXT,
                                   EPISODE    TEXT);''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS INDX_RSS_TORRENTS_NAME ON RSS_TORRENTS (TITLE, YEAR, SEASON, EPISODE);''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS INDX_RSS_TORRENTS_URL ON RSS_TORRENTS (ENCLOSURE);''')
            # 电影关键字表
            cursor.execute('''CREATE TABLE IF NOT EXISTS RSS_MOVIEKEYS
                                   (ID INTEGER PRIMARY KEY AUTOINCREMENT     NOT NULL,
                                   NAME    TEXT);''')
            # 电视剧关键字表
            cursor.execute('''CREATE TABLE IF NOT EXISTS RSS_TVKEYS
                                   (ID INTEGER PRIMARY KEY AUTOINCREMENT     NOT NULL,
                                   NAME    TEXT);''')
            # 豆瓣关注信息表
            cursor.execute('''CREATE TABLE IF NOT EXISTS DOUBAN_MEDIAS
                                   (ID INTEGER PRIMARY KEY AUTOINCREMENT     NOT NULL,
                                   NAME    TEXT,
                                   YEAR    TEXT,
                                   TYPE    TEXT,
                                   RATING   TEXT,
                                   IMAGE    TEXT,
                                   STATE    TEXT);''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS INDX_DOUBAN_MEDIAS_NAME ON DOUBAN_MEDIAS (NAME, YEAR);''')
            # 识别转移历史记录表
            cursor.execute('''CREATE TABLE IF NOT EXISTS TRANSFER_HISTORY
                                               (ID INTEGER PRIMARY KEY AUTOINCREMENT     NOT NULL,
                                               SOURCE    TEXT,
                                               MODE    TEXT,
                                               TYPE    TEXT,
                                               FILE_PATH    TEXT,
                                               FILE_NAME    TEXT,
                                               TITLE   TEXT,
                                               CATEGORY   TEXT,
                                               YEAR    TEXT,
                                               SE    TEXT,
                                               DEST    TEXT,
                                               DATE    );''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS INDX_TRANSFER_HISTORY_NAME ON TRANSFER_HISTORY (FILE_NAME);''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS INDX_TRANSFER_HISTORY_TITLE ON TRANSFER_HISTORY (TITLE);''')
            self.__connection.commit()
        except Exception as e:
            log.error("【DB】创建数据库错误：%s" % str(e))
        finally:
            cursor.close()

    def excute(self, sql):
        if not sql:
            return False
        cursor = self.__connection.cursor()
        try:
            cursor.execute(sql)
            self.__connection.commit()
        except Exception as e:
            log.error("【DB】执行SQL出错：%s，%s" % (sql, str(e)))
            return False
        finally:
            cursor.close()
        return True

    def select(self, sql):
        if not sql:
            return False
        cursor = self.__connection.cursor()
        try:
            res = cursor.execute(sql)
            ret = res.fetchall()
        except Exception as e:
            log.error("【DB】执行SQL出错：%s，%s" % (sql, str(e)))
            return []
        finally:
            cursor.close()
        return ret


def select_by_sql(sql):
    return DBHelper.get_instance().select(sql)


def update_by_sql(sql):
    return DBHelper.get_instance().excute(sql)


if __name__ == "__main__":
    print(select_by_sql("SELECT COUNT(1) FROM TRANSFER_HISTORY"))