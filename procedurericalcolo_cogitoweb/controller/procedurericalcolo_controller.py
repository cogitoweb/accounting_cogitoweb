import openerp.http as http
from openerp.http import request
import subprocess, os.path
from openerp.tools.config import config
from openerp.osv import fields, osv
import logging
_logger = logging.getLogger(__name__)
    

class ProcedureRicalcoloController(http.Controller):
    
    def getDbUser(self):
        dbUser = config.get("db_user")
        return dbUser
        
    def getDbPassword(self):
        dbPw = config.get("db_password")
        return dbPw
        
    def getDbPort(self):
        dbPort = config.get("db_port")
        return dbPort
        
    def getDbHost(self):
        dbHost = config.get("db_host")
        return dbHost    
    
    ## funzione privata
    def checkifSqlFunctionExists(self, cr, function_name):
        cr.execute("select exists(select * from pg_proc where proname = '" + function_name  + "');")        
        query_out = request.env.cr.fetchone()[0]           
        return query_out
    
    ## funzione privata
    def createSqlFunction(self, cr, function_name):
        ## info di db
        dbname = cr.dbname
        dbUser = self.getDbUser()
        dbPw = self.getDbPassword()
        dbPort = self.getDbPort()
        dbHost = self.getDbHost()
        _logger.info("_________________username: %s_____password: %s___________porta: %s___________host: %s_____________________________________",dbUser, dbPw, str(dbPort), str(dbHost))        
        ## info di filesystem
        relative_path = os.path.dirname(os.path.realpath(__file__))                
        if(not os.path.isfile(relative_path + "/../data/" + function_name + ".sql")):
            raise Exception('create function script ' + function_name + '.sql does not exist in data folder of this module')        
        ## controllo se function_name e creabile
        if(function_name == 'fix_parent'):
            subprocess.call(["psql", "postgresql://" + dbUser + ":" + dbPw + "@" + str(dbHost) + ":" + str(dbPort) + "/" + dbname, "-f", relative_path + "/../data/" + function_name + ".sql"])
            
            
        

    @http.route('/cogito_procedure/ricalcolo_piano_conti', type="json", auth="public")
    def ricalcolo_piano_conti(self):
        if(not self.checkifSqlFunctionExists(request.env.cr, 'fix_parent')):
            self.createSqlFunction(request.env.cr, 'fix_parent')    
        request.env.cr.execute("select fix_parent('account_account', 'parent_id', 'name')")        
        query_out = request.env.cr.fetchone()[0]        
        return {"query_out": query_out}
        
    @http.route('/cogito_procedure/ricalcolo_struttura_albero', type="json", auth="public")
    def ricalcolo_struttura_albero(self):
        if(not self.checkifSqlFunctionExists(request.env.cr, 'fix_parent')):
            self.createSqlFunction(request.env.cr, 'fix_parent')
            
        request.env.cr.execute("select fix_parent('account_account', 'parent_id', 'name')")        
        query_out = request.env.cr.fetchone()[0]        

        return {"query_out": query_out}