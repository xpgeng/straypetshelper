# -*- coding: utf-8 -*-
from fabric.api import env, run, local, settings
from datetime import datetime


def gitbranch(m='Commit something to branch...'):
	'''gitdev:m = "COMMIT LOGGING"\t(default as 'Commit something to dev...')
	'''	
	local('pwd'		    
		    '&& git add src'
		    '&& git commit -am "{msg}"'
		    '&& git push origin feature/web-framework'
		    '&& date'.format(msg = m)
        )


def gitmaster(f='src && README.md', m='Commit something to master...'):
	'''gitdev:f = "ADD FILENAMES"\t(default as 'src && README.md'), 
	          m = "COMMIT LOGGING"\t(default as 'Commit something to master...')
	'''	
	local('pwd'		    
		    '&& git add {filename}'
		    '&& git commit -am "{msg}"'
		    '&& git push origin feature/web-framework'
		    '&& date'.format(filename= f , msg = m )
        )