 #!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        Log.py
#
# Purpose:     This module is used to log the program execution information.(
#               info, warning, debug, error)
#
# Author:      Yuancheng Liu
#
# Created:     2020/07/13
# Copyright:   
# License:     
#-----------------------------------------------------------------------------
import os
import time
import logging
import logging.handlers
import traceback

DEFAULT_LOGGER_NAME = 'Log'
ROLLOVER_LENGTH = 1.0e7 + 1 # Python 'handlers' compares >= length(roll at 10MB)
# Init global parametersL
gLogger = None              # logger generator object
gHandler = None             # logging handler
gLogDir = None              # log directory path
gCrtDir = ''                # current log 
gPutLogsUnderDate = False   # flag to identify whether put log file under data folder.

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class RotateFileHandler(logging.handlers.RotatingFileHandler):
    """ Standard RotatingFileHandler makes a mess of file names that end in .txt 
        - this version inserts an index in between the name and the suffix.
    """
    def __init__(self, filename, *args, **kwargs):
        # filenameBase is just the base name - make up better name by adding date/time
        self.filenameBase = filename
        self.autoTReset = False # flag to identify whether auto reset filename time.
        self.crtTime = None     # Current time string.
        self.crtSuffix = 0      # Current Suffix index.
        fName = self.buildFilename(fResetTime=True)
        logging.handlers.RotatingFileHandler.__init__(self, fName, *args, **kwargs)

#--RotateFileHandler-----------------------------------------------------------
    def buildFilename(self, fResetTime=False):
        """ Generate the latest logfile's name based on the current time."""
        yyyymmdd, hhmmss = getLogTime()  # put in folder by today's date
        if fResetTime:
            # reset time part of name
            crtTime = yyyymmdd + '_' + hhmmss      # save creation date & time
            if self.crtTime != crtTime:
                self.crtSuffix = 0
            self.crtTime = crtTime
        self.crtSuffix += 1  # advance to next suffix
        fileName = self.filenameBase + '_' + self.crtTime + '_' + str(self.crtSuffix) + '.txt'
        pathName = getLogFilePath(yyyymmdd, fileName) if gPutLogsUnderDate else getLogFilePath(fileName)
        return pathName

#--RotateFileHandler-----------------------------------------------------------
    def doRollover(self, fResetTime=False):
        """ Handle rollover for TimedRotatingFileHandler. """
        if self.stream:
            self.stream.close()
            # in case someone still tries to write & opens file
            #self.baseFilename = 'TempBogusLog.txt'
        fResetTime = fResetTime or self.autoTReset
        self.baseFilename = self.buildFilename(fResetTime)
        self.mode = 'w'
        self.stream = self._open()

#--RotateFileHandler-----------------------------------------------------------
    def handleError(self, record):
        try:
            error('EXCEPTION in log: format str:"%s", args:%s' % (record.msg, record.args))
            stk = traceback.format_stack(limit=12)
            error('Traceback follows:\n' + ''.join(stk[:-8]))
        except Exception as e:
            error('Traceback has exception:%s', e)

#--RotateFileHandler-----------------------------------------------------------
    def setAutoTimeRest(self, fResetTime):
        """ Set the auto reset time flag for file name change during rotate."""
        self.autoTReset = fResetTime


#-----------------------------------------------------------------------------
# Module Logging functions.
#-----------------------------------------------------------------------------
def callstack(*args):
    """ Print compact callstack, with introductory string."""
    stk = traceback.extract_stack()
    debug(*args)
    for tup in stk[:-2]:
        fName, line, _, txt = tup
        debug('...%s:%i %s', os.path.split(fName)[1], line, txt)

#-----------------------------------------------------------------------------
def printArgs(*args):
    """ Call built in print function to show the arguments in cmd terminal."""
    s = args[0] % args[1:] if len(args) > 1 else args[0]
    print(s)

#-----------------------------------------------------------------------------
def info(*args, printFlag=None):
    """ Log normal information message: Log.info("message %s", str(value))"""
    if gLogger:
        gLogger.info(*args)
    elif printFlag is None or printFlag:
        printArgs(*args)

#-----------------------------------------------------------------------------
def warning(*args, printFlag=None):
    """ Log wanring message:  Log.wanring("message %s", str(value))"""
    if gLogger:
        gLogger.warning(*args)
    elif printFlag is None or printFlag:
        printArgs(*args)

#-----------------------------------------------------------------------------
def debug(*args, onFlag=True, printFlag=None):
    """ log debug message: Log.debug("message %s", str(value))"""
    if gLogger and onFlag:
        gLogger.debug(*args)
    elif printFlag is None or printFlag:
        printArgs(*args)

#-----------------------------------------------------------------------------
def error(*args, printFlag=None):
    """ Log error message: Log.debug("message %s", str(value))"""
    if gLogger:
        gLogger.error(*args)
    elif printFlag is None or printFlag:
        printArgs(*args)

#-----------------------------------------------------------------------------
def exception(*args, printFlag=None):
    """log exception message with the stack: Log.exception(e) """
    if gLogger:
        error('***** EXCEPTION >>>>>')
        error(*args)
        error(traceback.format_exc(limit=12))
        error('<<<<< EXCEPTION *****')
    elif printFlag is None or printFlag:
        print('***** EXCEPTION:')
        printArgs(*args)
        print(traceback.format_exc(limit=12))

#-----------------------------------------------------------------------------
def getLogTime(now=None):
    """ Get current local time, return tuple for logging (yyyymmdd, hhmmss)
        Can pass floating point time, or leave empty for 'now'
    """
    timeTuple = time.localtime() if now is None else time.localtime(now)
    tStr = time.strftime('%Y%m%d %H%M%S', timeTuple)
    return tStr.split()

#-----------------------------------------------------------------------------
def getLogFilePath(*args, logDir=None, folderFlg=False):
    """ Create the directory tree under the Log folder if necessary and finally
        return a fully qualified file name as string.
        - 'args' is a list of directories in the path to the filename in args[-1]
    """
    global gCrtDir, gLogDir
    if len(args) == 0:
        print("getLogFilePath: Must provide the log fileName.")
        return
    myArgs = [logDir] if logDir else [gLogDir]
    _ = myArgs.extend(args) if folderFlg else myArgs.extend(args[:-1])
    gCrtDir = os.path.join(*myArgs)
    if not os.path.exists(gCrtDir):
        os.makedirs(gCrtDir)
    filePath = gCrtDir if folderFlg else os.path.join(gCrtDir, args[-1])
    return filePath

#-----------------------------------------------------------------------------
gConsole = None
def setLogger(strm):
    """ Define a handler which writes INFO messages or higher to the specified
        stream.
        I had to change this for multiprocessing, to allow None for strm, to 
        remove handler for subprocesses (cannot write to main process' screen 
        in subprocess, so Log.info and Log.error, etc cannot be logged from 
        subprocesses)
        - strm: stream, such as ScreenLog.ScreenLog, where we can write high 
            priority messages
    """
    global gConsole
    if strm is None:
        # called from sub-process or terminate - want to remove previous logger
        if gConsole is not None:
            gConsole.setFormatter(None)
            gLogger.removeHandler(gConsole)
            gConsole = None
    else:
        gConsole = logging.StreamHandler(strm)
        gConsole.setLevel(logging.INFO)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(levelname)-8s %(message)s')
        # tell the handler to use this format
        gConsole.setFormatter(formatter)
        # add the handler to the root logger
        gLogger.addHandler(gConsole)


#-----------------------------------------------------------------------------
def cleanOldFiles(dirName, fileNameBase, cnt):
    """ Examine files in 'dirName', and if we find any that start with
        'fileNameBase', remove the oldest of those to keep no more
        than 'cnt' files in that dir
        This may be used for apps own logs, as well as the Log.xxx logs
    """

    log_list = []
    for f in os.listdir(dirName):
        # added every log file found into the log file list
        if f[0:len(fileNameBase)] == fileNameBase: log_list.append(f)
    if len(log_list) > cnt:     # if # of log files found more than the maximum number
        # set current working directory
        prevDir = os.getcwd()
        os.chdir(dirName)
        # sort the file list according to modification time
        log_list.sort(key=lambda x: (os.stat(x).st_mtime, x))
        # keep most recent log files and remove the old ones
        for i in range(len(log_list) - cnt):
            try:
                #print('Log.cleanOldFiles deleted: ', log_list[i])
                os.remove(log_list[i])
            except Exception:
                warning('Log: cleanOldFiles could not delete <%s>', log_list[i])
        os.chdir(prevDir)

#-----------------------------------------------------------------------------
def initLogger(pwd, logDirName, appName, filePrefix, historyCnt=100,
        fPutLogsUnderDate=False, loggerName=DEFAULT_LOGGER_NAME, autoRestTime=False):
    """ Initialize logging
        - pwd: pathname of working directory under which we put logs
        - logDirName: put all logs into this dir, i.e. 'Logs'
        - appName: make subdir under LogDirName for this app.
        - filePrefix: prefix for log files, i.e. 'Hub'
        - historyCnt: # of log files to save (delete oldest if >this many files)
        - fPutLogsUnderDate: if True, we arrange to put log files into a daily
            folder, otherwise, they go directly into the Logs folder.
        - loggerName: name of this logger.
    """
    global gLogger, gHandler, gLogDir, gPutLogsUnderDate 
    assert pwd is not None       # caller must set this up
    try:
        if gLogger is not None:
            # handling reinitializing
            try:
                gLogger.removeHandler(gHandler)
                del gLogger
            except Exception:
                exception('initLogger:  Log could not delete gLogger')
            gLogger = None
            gHandler = None
        gPutLogsUnderDate = fPutLogsUnderDate

        gLogDir = getLogFilePath(logDirName, appName, logDir=pwd, folderFlg=True) if appName else getLogFilePath(
            logDirName, logDir=pwd, folderFlg=True)

        gLogger = logging.getLogger(loggerName)
        gHandler = RotateFileHandler(filePrefix, maxBytes=ROLLOVER_LENGTH)
        gHandler.setFormatter(logging.Formatter(
            '%(asctime)-15s %(levelname)-8s %(message)s'))
        gHandler.setAutoTimeRest(autoRestTime)
        gLogger.addHandler(gHandler)
        gLogger.setLevel(logging.DEBUG)

    except Exception as e:
        print('Logging setup exception:', e)

    # parse the directory to look for all the log files
    cleanOldFiles(os.path.dirname(gHandler.baseFilename), filePrefix, historyCnt)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def writeTest(mb=10):
    """Write 'mb' megabytes of junk to log"""
    print('writeTest messages:  %iMB' % mb)
    lineLen = 100
    hdrLen = 33 + 7 + 1        # header per line, plus len of line #, plus lf
    pad = '$' * (lineLen - hdrLen)
    for i in range((mb * 1000000) // lineLen//4):
        info('%06i %s', i, pad)
        warning('%06i %s', i, pad)
        debug('%06i %s', i, pad)
        error('%06i %s', i, pad)

def testCase():
    TOPDIR = 'Log'                      # folder name where we put Logs, Maps, etc
    gWD = os.getcwd()
    #print('gWD:%s' % gWD)
    idx = gWD.find(TOPDIR)
    #print('idx:%i' % idx)
    if idx != -1:
        gTopDir = gWD[:idx + len(TOPDIR)]     # found it - truncate right after TOPDIR
    else:
        gTopDir = gWD   # did not find TOPDIR - use WD
    print('gTopDir:%s' % gTopDir)
    logSz = 15  # create 15 MB logfiles.

    initLogger(gTopDir, 'Logs', 'LogTest1', 'Test',
               historyCnt=100, 
               fPutLogsUnderDate=True)
    writeTest(logSz)

    time.sleep(1)
    initLogger(gTopDir, 'Logs', 'LogTest2', 'Test', 
                historyCnt=5,
                fPutLogsUnderDate=False, 
                autoRestTime=True)
    writeTest(logSz)
    pass

if __name__ == '__main__':
    testCase()
    print('End of __main__')
