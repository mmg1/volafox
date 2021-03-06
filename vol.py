#!/usr/bin/env python                       # LSOF: new path
#!c:\python\python.exe
# -*- coding: utf-8 -*-
#  -*- mode: python; -*-

# volafox
# Copyright by n0fate - rapfer@gmail.com, volafox@n0fate.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

import getopt
import sys

from volafox.volafox import volafox

def usage():
    
    print ''
    print 'volafox: Mac OS X Memory Analysis Toolkit'
    print 'project: https://github.com/n0fate/volafox'
    print 'support: 10.6-11(Snow Leopard ~ El Capitan); 32/64-bit kernel'
    print '  input: raw memory image (*.mem or exported raw memory image using rekal developed by google'
    print '  -> If you get a AFF4 format, you can export linear memory image as following cmd : rekal aff4export -D . [AFF4 MEMORY IMAGE]'
    print ''
    print '  usage: python %s -i IMAGE [-o COMMAND [-vp PID][-x PID][-x KEXT_ID][-x TASKID][-x SYMFILENAME]]\n' %sys.argv[0]
    
    print 'Options:'
    print '-o CMD            : Print kernel information for CMD (below)'
    print '-p PID            : List open files for PID (where CMD is "lsof" and dumpfile)'
    print '-v                : Print all files, including unsupported types (where CMD is "lsof")'  
    print '-x PID/KID/TASKID/SYMBOLNAME/Virtual ADDRESS :'
    print '   Dump process/task/kernel extension address space for PID/KID/Task ID (where CMD is "ps"/"kextstat"/"tasks"/"machdump"/"dumpsym"/"dumpfile")\n'
    
    print 'COMMANDS:'
    print 'system_profiler : Kernel version, CPU, and memory spec, Boot/Sleep/Wakeup time'
    print 'mount           : Mounted filesystems'
    print 'kextstat        : KEXT (Kernel Extensions) listing'
    print 'kextscan        : Scanning KEXT (Kernel Extensions) (64bit OS only)'
    print 'ps              : Process listing'
    print 'tasks           : Task listing (Finding process hiding)'
    print 'machdump        : Dump macho binary (experiment)'
    print 'systab          : Syscall table (Hooking detection)'
    print '                  => Call Number 427 is bugged not hooked.'
    print 'mtt             : Mach trap table (Hooking detection)'
    print 'netstat         : Network socket listing (Hash table)'
    print 'lsof            : Open files listing by process (research, osxmem@gmail.com)'    # LSOF: new lsof command
    print 'dumpfile        : Dump a file on Memory (Required -p and -x option)'
    print 'pestate         : Show Boot information'
    print 'efiinfo         : EFI System Table, EFI Runtime Services'
    print 'keychaindump    : Dump master key candidates for decrypting keychain(Lion ~ El Capitan)'
    print 'getfvkey        : Dump Filevault2 Volume Masker Key (Thomas White\'s idea)'
    print 'dmesg           : Debug message at boot time'
    print 'uname           : Print a short for unix name(uname)'
    print 'hostname        : Print a hostname'
    print 'notifiers       : Detects I/O Kit function hooking'
    print 'trustedbsd      : Show TrustedBSD MAC Framework'
    print 'bash_history    : Show history in bash process'
    print 'sysctl          : show the result like sysctl command'
    print 'dumpsym         : Dump kernel symbol address considered of KASLR to file (for RCE)'
    print ''
    print 'Kernel Rootkit Detection: (testing code by n0fate) - Required Library : distorm3'
    print 'kdebug_hook     : Examination of the KDebug function code for mal-code detection'
    print 'kauth_hook      : Examination of the KAUTH for mal-code hiding detection from Anti-virus'
    print 'bsm_hook        : Examination of auto_commit function on the OpenBSM'
    print 'fbt_syscall     : Examination of syscall table for hooking by DTrace FBT Provider'
#    print 'net_info_test\t network information(plist), (experiment)'

def main():
    mempath = ''
    oflag = ''
    pflag = 0           # LSOF: new pid flag
    vflag = 0           # LSOF: show debugging output and experimental options for lsof
    dflag = 0
    mflag = 0   
    tflag = 0           # task dump option
    pid = -1            # LSOF: relocated this definition
    offset = 0          # dumpfile
    #callie = ''
    filename = ''
    physaddr = 0        # physical address for findphysowner plugin

    try:
        # LSOF: added -p flag for pid specification with lsof, -v no longer needs arg
        #option, args = getopt.getopt(sys.argv[1:], 'o:i:x:v:m:')
        option, args = getopt.getopt(sys.argv[1:], 'o:i:x:vp:f:')

    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit()

    debug = ""  # LSOF: debug string, print only with -v flag
    
    for op, p, in option:
        if op in '-o':  # data type
        
            # LSOF: add to debug string, no newline so -p can be added
            #print '[+] Information:', p
            debug += "[+] Command: %s" %p
            
            oflag = p
            
            # LSOF: new pid flag
            #suboption = option
            for i,x in enumerate(option):
                if p == 'lsof' and x[0] == '-p':
                    pid = int(x[1], 10)
                    pflag = 1;
                    debug += " -p %d" %pid
                    break

                elif p == 'dumpfile' and x[0] == '-p':
                    pid = int(x[1], 10)
                    debug += " -p %x" %offset

                elif p == 'dumpfile' and x[0] == '-x':
                    offset = int(x[1], 16)
                    debug += " -x %x" %offset

                elif p == 'ps' and x[0] == '-x': # process dump
                    pid = int(x[1], 10)
                    debug += ' -x %d' %pid
                    dflag = 1
                    break

                elif p == 'inline_quick' and x[0] == '-x':  # function name
                    pid = str(x[1])
                    debug += ' -x %s' %pid
                    break

                elif p == 'findphysowner' and x[0] == '-x':  # function name
                    physaddr = str(x[1])
                    debug += ' -x %s' %physaddr
                    break
        
                elif p == 'machdump' and x[0] == '-x': # process dump
                    pid = int(x[1], 10)
                    debug += ' -x %d' %pid
                    break

                elif p == 'kextstat' and x[0] == '-x': # kext dump
                    kext_num = int(x[1], 10)
                    debug += ' -x %d' %kext_num
                    mflag = 1
                    break

                elif p =='dumpsym' and x[0] == '-x': # kext dump
                    filename = str(x[1])
                    debug += ' -x %s' %filename
                    break

                elif p == 'tasks' and x[0] == '-x': # task dump
                    task_id = int(x[1], 10)
                    debug += ' -x %d' %task_id
                    tflag = 1
                    break

                    del option[i]
                    del option[x]
                    debug += "\n"   # LSOF: replacing newline

        elif op in '-i': # physical memory image file
        
            # LSOF: add to debug string
            #print '[+] Memory Image:', p
            debug += '[+] Memory Image: %s\n' %p
            
            mempath = p

        # LSOF: reworked this, it appears to have been unused (now shows debug string)
        elif op == '-v': # verbose
            #print 'Verbose:', p
            vflag = 1
           
        #else:
        #    print '[+] Command error:', op # LSOF: not printed, getopt catches this
        #    usage()
        #    sys.exit()
            
    # LSOF: all of this information now requires an explicit flag (or command error)
    if vflag:
        print debug

    if mempath == "" and ( oflag == "" or dflag == 0 or mflag == 0):
        usage()
        sys.exit()

    # Auto switching code for using overlays or original mach-o files.  We should autopickle
    # using the original file.
    m_volafox = volafox(mempath)

    ## get kernel version, architecture ##
    
    # LSOF: pass the verbose flag so debugging information can be optionally printed
    overlay_path = m_volafox.get_kernel_version(vflag) # ret: true/false , overlay filepath
    if overlay_path == '':
        print '[+] WARNING: Can not found image information'
        sys.exit()

    ret_loader = m_volafox.overlay_loader(overlay_path, vflag)
    if ret_loader == 1:
        sys.exit()

    ## Setting Page Table Map
    nRet = m_volafox.init_vatopa_x86_pae(vflag)
    if nRet == 1:
        print "[+] WARNING: Memory Image Load Failed"
        sys.exit()

    if mflag == 1:
        m_volafox.kextdump(kext_num)
        sys.exit()
        
    if dflag == 1:
        m_volafox.proc_dump(pid)
        sys.exit()
    
    if tflag == 1:
        m_volafox.task_dump(task_id)
        sys.exit()

    # test
    if oflag == 'get_phy':
        m_volafox.get_vtop(0xffffff8000b210f8)
        sys.exit()

    if oflag == 'system_profiler':
        m_volafox.get_system_profiler()
        sys.exit()

    elif oflag == 'kextstat':
        m_volafox.kextstat()
        sys.exit()

    elif oflag == 'mount':
        data_list = m_volafox.mount()
        sys.exit()

    elif oflag == 'ps':
        m_volafox.get_ps()
        sys.exit()
    
    elif oflag == 'tasks':
        m_volafox.get_tasks()
        sys.exit()

    elif oflag == 'machdump':
        m_volafox.machdump(pid)
        sys.exit()
        
    # LSOF: lsof command branch
    elif oflag == 'lsof':
        if vflag:
            print ""    # separate output from command specification
        filelist = m_volafox.lsof(pid, vflag)
        sys.exit()

    elif oflag == 'dumpfile':
        if not(offset) or not(pid):
            print 'Check a dumpfile option'
            return
        if vflag:
            print ""
        m_volafox.dumpfile(offset, pid, vflag)

    elif oflag == 'systab':
        m_volafox.systab()
        sys.exit()
    
    elif oflag == 'mtt':
        m_volafox.mtt()
        sys.exit()

    elif oflag == 'netstat':
        m_volafox.netstat()
        sys.exit()

    # elif oflag == 'netstat_test':
    #     m_volafox.netstat_test()
    #     sys.exit()
    
    elif oflag == 'pestate':
        m_volafox.pe_state()
        sys.exit()

    elif oflag == 'efiinfo':
        m_volafox.efi_system_table()
        sys.exit()
        
    elif oflag == 'keychaindump':
        m_volafox.keychaindump()
        sys.exit()

    elif oflag == 'bash_history':
        m_volafox.bash_history()
        sys.exit()        
    
    elif oflag == 'kextscan':
        m_volafox.kextscan()
        sys.exit()
    
    elif oflag == 'dmesg':
        m_volafox.dmesg()
        sys.exit()
    
    elif oflag == 'uname':
        m_volafox.uname()
        sys.exit()
    
    elif oflag == 'hostname':
        m_volafox.hostname()
        sys.exit()

    elif oflag == 'notifiers':
        m_volafox.notifier()
        sys.exit()

    elif oflag == 'trustedbsd':
        m_volafox.trustedbsd()
        sys.exit()

    elif oflag == 'fbt_syscall':
        m_volafox.fbt_syscall()
        sys.exit()

    elif oflag == 'inline_quick':
        print 'func : %s'%pid
        m_volafox.inline_quick(pid)
        sys.exit()

    elif oflag == 'findphysowner':
        if not physaddr:
            usage()
            sys.exit()
        m_volafox.findphysaddr_owner(physaddr)
        sys.exit()

    elif oflag == 'bsm_hook':
        m_volafox.find_bsm_hook()
        sys.exit()

    elif oflag == 'kauth_hook':
        m_volafox.find_kauth_hook()
        sys.exit()

    elif oflag == 'kdebug_hook':
        m_volafox.find_kdebug_hook()
        sys.exit()

    elif oflag == 'dumpsym':
        if len(filename) == 0:
            print '[+] WARNING: -x Argument Error. Please enter dump file name(-x option)'
            sys.exit()
        m_volafox.export_symbol_table(filename)
        sys.exit()

    elif oflag == 'dumpcomppage':
        m_volafox.dumpcompsegment()
        sys.exit()

    elif oflag == 'sysctl':
        m_volafox.checksysctl()
        sys.exit()

    elif oflag == 'getfvkey':
        m_volafox.dumpfilevaultkey()
        sys.exit()

    else:
        print '[+] WARNING: -o Argument Error: %s\n'%oflag
        usage()
        sys.exit()

if __name__ == "__main__":
    main()
