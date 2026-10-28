"""Build bounded Java 5 OSGi worker with no external toolchain."""
import struct,sys,zipfile
from pathlib import Path

def u2(n):return struct.pack('>H',n)
def u4(n):return struct.pack('>I',n)
class CP:
 def __init__(self):self.items=[]
 def add(self,x):self.items.append(x);return len(self.items)
 def utf(self,s):
  x=s.encode();return self.add(b'\1'+u2(len(x))+x)
 def cls(self,s):return self.add(b'\7'+u2(self.utf(s)))
 def string(self,s):return self.add(b'\10'+u2(self.utf(s)))
 def nt(self,n,d):return self.add(b'\x0c'+u2(self.utf(n))+u2(self.utf(d)))
 def ref(self,tag,c,n,d):return self.add(bytes([tag])+u2(self.cls(c))+u2(self.nt(n,d)))
 def method(self,c,n,d):return self.ref(10,c,n,d)
 def field(self,c,n,d):return self.ref(9,c,n,d)

def build(output,helper,interval):
 c=CP(); this=c.cls('h2ap/Worker');sup=c.cls('java/lang/Object');i1=c.cls('org/osgi/framework/BundleActivator');i2=c.cls('java/lang/Runnable');thr=c.cls('java/lang/Thread');exc=c.cls('java/lang/Exception')
 code=c.utf('Code');init_n=c.utf('<init>');void=c.utf('()V');ctx=c.utf('(Lorg/osgi/framework/BundleContext;)V');start_n=c.utf('start');stop_n=c.utf('stop');run_n=c.utf('run');runfield_n=c.utf('running');booldesc=c.utf('Z');threadfield_n=c.utf('worker');threaddesc=c.utf('Ljava/lang/Thread;')
 init=c.method('java/lang/Object','<init>','()V');f_run=c.field('h2ap/Worker','running','Z');f_worker=c.field('h2ap/Worker','worker','Ljava/lang/Thread;');threadinit=c.method('java/lang/Thread','<init>','(Ljava/lang/Runnable;)V');daemon=c.method('java/lang/Thread','setDaemon','(Z)V');threadstart=c.method('java/lang/Thread','start','()V');interrupt=c.method('java/lang/Thread','interrupt','()V');join=c.method('java/lang/Thread','join','(J)V');sleep=c.method('java/lang/Thread','sleep','(J)V');get=c.method('java/lang/Runtime','getRuntime','()Ljava/lang/Runtime;');execute=c.method('java/lang/Runtime','exec','(Ljava/lang/String;)Ljava/lang/Process;');wait=c.method('java/lang/Process','waitFor','()I')
 cmds=[c.string(helper+' '+port+' 1') for port in ('wlan0','wlan4','eth2')];assert max(cmds)<256 and 1<=interval<=32767
 def meth(name,desc,body,stack,locals,handlers=[]):
  h=b''.join(u2(a)+u2(b)+u2(d)+u2(e) for a,b,d,e in handlers)
  data=u2(stack)+u2(locals)+u4(len(body))+body+u2(len(handlers))+h+u2(0)
  return u2(1)+u2(name)+u2(desc)+u2(1)+u2(code)+u4(len(data))+data
 ins_init=b'\x2a\xb7'+u2(init)+b'\xb1'
 ins_start=(b'\x2a\x04\xb5'+u2(f_run)+b'\x2a\xbb'+u2(thr)+b'\x59\x2a\xb7'+u2(threadinit)+b'\xb5'+u2(f_worker)+b'\x2a\xb4'+u2(f_worker)+b'\x04\xb6'+u2(daemon)+b'\x2a\xb4'+u2(f_worker)+b'\xb6'+u2(threadstart)+b'\xb1')
 ins_stop=(b'\x2a\x03\xb5'+u2(f_run)+b'\x2a\xb4'+u2(f_worker)+b'\xb6'+u2(interrupt)+b'\x2a\xb4'+u2(f_worker)+b'\x11\x03\xe8\x85\xb6'+u2(join)+b'\xb1')
 # Conditional branches are relative to the branch opcode.
 body=bytearray(b'\x2a\xb4'+u2(f_run));branch=len(body);body+=b'\x99\x00\x00';try_begin=len(body)
 for v in cmds:body+=b'\xb8'+u2(get)+b'\x12'+bytes([v])+b'\xb6'+u2(execute)+b'\xb6'+u2(wait)+b'\x57'
 body+=b'\x11'+u2(interval)+b'\x85\xb8'+u2(sleep);endtry=len(body);back=len(body);body+=b'\xa7'+struct.pack('>h',-back)
 handler=len(body);body+=b'\x57\x2a\x03\xb5'+u2(f_run)+b'\xb1';end=len(body);body+=b'\xb1';body[branch+1:branch+3]=struct.pack('>h',end-branch)
 fields=u2(2)+u2(0x42)+u2(runfield_n)+u2(booldesc)+u2(0)+u2(2)+u2(threadfield_n)+u2(threaddesc)+u2(0)
 methods=[meth(init_n,void,ins_init,1,1),meth(start_n,ctx,ins_start,4,2),meth(stop_n,ctx,ins_stop,3,2),meth(run_n,void,bytes(body),2,1,[(try_begin,endtry,handler,exc)])]
 klass=b'\xca\xfe\xba\xbe'+u2(0)+u2(49)+u2(len(c.items)+1)+b''.join(c.items)+u2(0x21)+u2(this)+u2(sup)+u2(2)+u2(i1)+u2(i2)+fields+u2(len(methods))+b''.join(methods)+u2(0)
 manifest=('Manifest-Version: 1.0\r\nBundle-ManifestVersion: 2\r\nBundle-SymbolicName: local.h2ap.worker\r\nBundle-Version: 1.0.0\r\nBundle-Activator: h2ap.Worker\r\nImport-Package: org.osgi.framework\r\n\r\n').encode()
 with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED) as z:z.writestr('META-INF/MANIFEST.MF',manifest);z.writestr('h2ap/Worker.class',klass)
if __name__=='__main__':build(Path(sys.argv[1]),sys.argv[2],int(sys.argv[3]))
