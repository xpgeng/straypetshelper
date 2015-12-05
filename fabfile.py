# -*- coding: utf-8 -*-
from fabric.api import env, run, local, settings
from datetime import datetime




def gitmaster(m='Commit something to master...'):
	'''gitmaster:m = "COMMIT LOGGING"\t(default as 'Commit something...')
	'''	
	local('pwd'		    
		    '&& git add .'
		    '&& git commit -am "{msg}"'
		    '&& git push origin master'
		    '&& date'.format(msg = m)
        )

def gitdev(m='Commit something to dev...'):
	'''gitdev:m = "COMMIT LOGGING"\t(default as 'Commit something to dev...')
	'''	
	local('pwd'		    
		    '&& git add .'
		    '&& git commit -am "{msg}"'
		    '&& git push origin dev'
		    '&& date'.format(msg = m)
        )
