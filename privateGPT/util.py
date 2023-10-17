import os
import logging as log

def prepare_dir(job_uuid, projpath='', rootdir='./'):
    error = None
    try:
        fullprojpath = rootdir + os.path.sep + job_uuid
        os.mkdir(fullprojpath)
    except Exception as e:
        error = str(e)
        log.info('ignoring base user directory if it exists' + str(fullprojpath))
    try:
        if projpath:
            fullprojpath = rootdir + os.path.sep + projpath + os.path.sep + job_uuid
            log.info('making sure user job directory exists')
            os.mkdir(fullprojpath)
    except Exception as e:
        error = str(e)
        log.error(str(e))
    finally:
        return fullprojpath, error