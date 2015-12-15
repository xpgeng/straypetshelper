# -*- coding: utf-8 -*-
from fabric.api import env, run, local, settings
from datetime import datetime


def gitmaster(m='Commit something to master...'):
	'''gitmaster:f = "ADD FILENAMES"\t(default as 'src && README.md'), 
	          m = "COMMIT LOGGING"\t(default as 'Commit something to master...')
	'''	
	local('pwd'		    
		    '&& git add -A'
		    '&& git commit -am "{msg}"'
		    '&& git push sae master:1'
		    '&& date'.format(msg = m )
        )