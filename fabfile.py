# -*- coding: utf-8 -*-
from fabric.api import env, run, local, settings
from datetime import datetime


def gitbranch(m='Commit something to dev...'):
	'''gitdev:m = "COMMIT LOGGING"\t(default as 'Commit something to dev...')
	'''	
	local('pwd'		    
		    '&& git add src'
		    '&& git commit -am "{msg}"'
		    '&& git push origin feature/web-framework'
		    '&& date'.format(msg = m)
        )
