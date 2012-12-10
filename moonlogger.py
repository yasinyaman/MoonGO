#-*- coding:utf-8 -*-

import time

class Logger(object):
    def __init__(self,connection=None,pr=2):
        """
            pr=2 hem db'ye hem print
            pr=1 sadece db'ye
            pr=0 sadece print
        """
        self.con = connection
        if not self.con and pr is not 0:
            print "Error: Location: moonlogger.Logger.__init__, Exception: Connection Error, Time: %s" % str(time.time())

        self.pr = pr

        self.pr_data = "%%s: Location: %%s, Exception: %%s, Time: %%s"

    def _set_data(self,loc,exp,type,extra,pr):
        """
        loc: logun kaydedildiği yer - dosya.class.fonksiyon
        exp: logun kaydedilme nedeni - try-except'te alınan hata olabilir
        type: logun seviyesi - error, warning, info
        extra: loga eklenmek istenen extra mesaj
                - locta fonksiyon çok uzunsa buraya değişken ismi verilebilir
                - mesela _set_data >= 200 satır
                - error("moonlogger.Logger._set_data",str(e),extra="t=time.time()"
        pr: __init__ 'de var.
        """
        if not pr: pr = self.pr
        t = time.time()
        data = {
            "location":"%s" % loc,
            "exception":"%s" % exp,
            "time":"%s" % t,
            "type":"%s" % type
        }
        pr_data = "%s:: Location: %%s, Exception: %%s, Time: %s" % (type.capitalize(),t)

        if extra:
            data["extra"] = extra
            pr_data += ", Extra: %s" % extra

        if pr == 2:
            self.con.moongo_sys.logger.insert(data)
            print(pr_data % (loc, exp))
        elif pr == 1:
            self.con.moongo_sys.logger.insert(data)
        else:
            print (pr_data % (loc,exp))

    def error(self,loc,exp,extra=None,pr=None):
        self._set_data(loc,exp,"error",extra,pr)

    def warning(self,loc,exp,extra=None,pr=None):
        self._set_data(loc,exp,"warning",extra,pr)

    def info(self,loc,exp,extra=None,pr=None):
        self._set_data(loc,exp,"info",extra,pr)