import sys, os, fcntl, errno, pprint
import _kmsg
import argparse

__author__ = "maliubiao<maliubiao@gmail.com>"
__status__ = "production"
__version__ = "0.01"
__date__ = "23 Febrary 2014"

klogctl = _kmsg.klogctl

#close the log
SYSLOG_CLOSE  = 0
#open the log
SYSLOG_OPEN = 1
#read from the log
SYSLOG_READ = 2
#read all messages remainning in the ring buffer, (allowed for non-root)
SYSLOG_READ_ALL = 3
#read and clear all messages remaining in the ring buffer */
SYSLOG_READ_CLEAR = 4
#clear ring buffer
SYSLOG_CLEAR = 5
#disable printk's to console
SYSLOG_CONSOLE_OFF = 6
#enable printk's to console
SYSLOG_CONSOLE_ON = 7
#set level of messages printed to console
SYSLOG_CONSOLE_LEVEL = 8
#return number of unread characters in the log buffer
SYSLOG_SIZE_UNREAD = 9
#return size of the log buffer
SYSLOG_SIZE_BUFFER = 10

#log level
LOG_EMERG, LOG_ALERT, LOG_CRIT, LOG_ERR, LOG_WARN, LOG_NOTICE, LOG_INFO, LOG_DEBUG = range(8)

#facility codes
LOG_KERN, LOG_USER, LOG_MAIL, LOG_DAEMON, LOG_AUTH, LOG_SYSLOG, LOG_LPR, LOG_NEWS, LOG_UUCP, LOG_CRON, LOG_AUTHPRIV, LOG_FTP = [x<<3 for x in range(12)]

log_level_dict = {
        LOG_EMERG: ("emerg", "system is unusable"),
        LOG_ALERT: ("alert", "action must be taken immediately"),
        LOG_CRIT: ("crit", "critical conditions"),
        LOG_ERR: ("err", "error conditions"),
        LOG_WARN: ("warn", "warning conditions"),
        LOG_NOTICE: ("notice", "normal but significant condition"),
        LOG_INFO: ("info", "information"),
        LOG_DEBUG: ("debug", "debug-level message")
        }

log_dict = dict([(y[0], x) for x, y in log_level_dict.items()])
       

facility_codes_dict = {
        LOG_KERN: ("kernel", "kernel messages"),
        LOG_USER: ("user", "random user-level messages"),
        LOG_MAIL: ("mail", "mail system"),
        LOG_DAEMON: ("daemon", "system daemons"),
        LOG_AUTH: ("auth", "security/authorization messages"),
        LOG_SYSLOG: ("syslog", "messages generated internally by syslogd"),
        LOG_LPR: ("lpr", "line printer subsystem"),
        LOG_NEWS: ("news", "network news subsystem"),
        LOG_UUCP: ("uucp", "UUCP subsystem"),
        LOG_CRON: ("cron", "clock daemon"),
        LOG_AUTHPRIV: ("authpriv", "security/authorization messages (private)"),
        LOG_FTP: ("ftp", "ftp daemon")
        }

fac_dict = dict([(y[0], x) for x, y in facility_codes_dict.items()])


LOG_NO_PRI = 0x10 

BUF_SIZE = 512
#bits 0-2-> pri,  high bits -> facility

def log_pri(p):
    return p & 0x07

def log_fac(p):
    return (p & 0x03f8) >> 3

def log_make_pri(fac, pri):
    return fac | pri

OPTION_KMSG, OPTION_SYSLOG, OPTION_MMAP = range(3)

def parse_msg(msg): 
    '''
    /dev/kmsg record format:
        faclev,seqnum,timestamp[optional,..];message\n
         TAGNAME=value
         ...
    ''' 
    #msg header and body
    header_loc = msg.find(";")
    header = msg[:header_loc]
    msg = msg[header_loc+1:] 
    #msg header
    fac, seq, time, other = header.split(",") 
    header = header.split(",") 
    facpri = int(header[0])
    seq = int(header[1])
    time = int(header[2])
    other = ",".join(header[3:]) 
    #tags
    tags_loc = msg.find("\n")
    tags = msg[tags_loc+1:]
    msg = msg[:tags_loc]
    tags_dict = {} 
    if tags: 
        for tag in tags.split("\n"): 
            if not tag:
                continue
            k, v = tag[1:].split("=")
            tags_dict[k] = v
    else:
        tags_dict = None 
    return {
        "fac": log_fac(facpri),
        "pri": log_pri(facpri),
        "seqnum": seq,
        "timestamp": time,
        "other": other,
        "msg": msg,
        "tags": tags_dict
        } 

def read_kmsg(): 
    f = open("/dev/kmsg", "r")
    fd = os.dup(f.fileno())
    f.close() 
    fcntl.fcntl(fd, fcntl.F_SETFL, os.O_NONBLOCK)
    msgs = []
    while True:
        try:
            msg = os.read(fd, BUF_SIZE)
        except OSError as e:
            if e.errno == errno.EAGAIN:
                break
            else:
                raise e 
        msgs.append(parse_msg(msg))
    os.close(fd) 
    return msgs

def filter_pri(msgs, pri):
    ret = []
    for i in msgs:
        if i["pri"] == pri:
            ret.append(i)
    return ret

def filter_fac(msgs, fac):
    ret = []
    for i in msgs:
        if i["pri"] == pri:
            ret.append(i)
    return ret 


def main():
    parser = argparse.ArgumentParser(
        description="a klog filter")
    parser.add_argument("-p", type=str, help="filter by pri")
    parser.add_argument("-f", type=str, help="filter by fac")
    args = parser.parse_args() 
    if args.p:
        msgs = read_kmsg() 
        if args.p in log_dict:
            pprint.pprint(filter_pri(msgs, log_dict[args.p]))
        else:
            print "unknown log level"
    if args.f:
        msgs = read_kmsg() 
        if args.f in fac_dict: 
            pprint.pprint(filter_fac(msgs, fac_dict[args.p])) 
        else:
            print "unknown facility"

if __name__ == "__main__":
    main()
