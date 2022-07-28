import json
import os,shutil
from collections import OrderedDict
import datetime
from functools import wraps


# ===== Utility
defaultname = "z.log.json"

datetimeformat = "%Y-%m-%dT%H-%M-%S"
dateformat = "%Y-%m-%d"
def now(obj = False):
  """ return current datetime
  Args:
    obj (bool): True --> return datetime object, False --> return string (default)
  """
  if obj:
    return datetime.datetime.now()
  else:
    return datetime.datetime.now().strftime(datetimeformat)

def today(obj = False):
  """ return today's date
  Args:
    obj (bool): True --> return datetime object, False --> return string (default)
  """
  if obj:
    return datetime.date.today()
  else:
    return datetime.date.today().strftime(dateformat)

# one-liner wrapper for json
# without all the validation
def json_load(filename):
    with open(filename,'r') as f:
        d0 = json.load(f,object_pairs_hook = OrderedDict)
    return d0
def json_write(filename,d0):
    tmp = "tmp_"+filename
    try:
        with open(tmp,'w') as f:
            json.dump( d0, f, indent=2 ) 
        shutil.move(tmp,filename)
    except:
        raise ValueError("Problem dumping json, see {}".format(tmp))

# decorator, basic standard logging
def log_this(field,filename=None,msg=None):
    if filename is None:
        filename = defaultname
    def inner_decorator(field,msg):
        """creates decorator that logs the return value"""
        @wraps(func)
        def logged_function(field=None,*args,**kwargs):
            d = func(*args,**kwargs)
            log(d,filename=filename,msg=msg)
        return logged_function

    return inner_decorator

# ===== Logging
def log(d=None,filename=defaultname,msg=None,verbose=False):
    """directly writes to log; no intermediate dictionary object returned"""
    d0 = load(filename)

    changes = []
    if d is not None:
      for k,v in d.items():
          if k in d0:
              if v != d0[k]:
                  d0[k] = v
                  if verbose:
                    changes.append("updated {} -> {}".format(str(k),str(v)))
                  else:
                    changes.append("updated {}".format(str(k)))
          else:
              if verbose:
                  changes.append("added {} ({})".format(str(k),str(v)))
              else:
                  changes.append("added {}".format(str(k)))
              d0[k] = v

    note = "; ".join(changes)
    if msg is not None:
        note = msg + "; " + note
        
    if note != "":
        print(note)
        #timestamp = now()
        #d0['history'].append((timestamp,note))
        log_history(d0,note)
    else:
        print("nothing changed in log")

    #Try writing first, or else will erase current log if the write fails:
    writeable = False
    try:
        with open("tmplog.json","w") as f:
            json.dump( d0, f, indent=2 )
        writeable = True
        os.remove("tmplog.json")
    except:
        print("write failed, see tmplog.json")
        raise 

    if writeable:
        with open(filename,'w') as f:
            json.dump( d0, f, indent=2 ) 


def log_history(d0,note,timestamp=None):
    """save note to history of a given dictionary"""
    if timestamp is None:
        timestamp = now()
    d0['history'].append((timestamp,note))

def remove(k,filename=defaultname,msg="",verbose=False):
    d0 = load(filename)
    if k in d0:
      val = d0.pop(k)
      if verbose:
          note = "popped key {}".format(k)
      else:
          note = "popped key {} storing: {}".format(k,val)
   
    if msg == "":
      msg = note
    else:
      msg = msg + "; " + note 
    log_history(d0,note)

    #Try writing first, or else will erase current log if the write fails:
    writeable = False
    try:
      with open("tmplog.json","w") as f:
        json.dump( d0, f, indent=2 )
      writeable = True
      os.remove("tmplog.json")
    except:
      print("write failed, see tmplog.json")
      raise 

    if writeable:
      with open(filename,'w') as f:
        json.dump( d0, f, indent=2 ) 

def load(filename=defaultname):
    if os.path.exists(filename):
        with open(filename,'r') as f:
            d0 = json.load(f,object_pairs_hook = OrderedDict)
    else:
        print('Log not found, starting a new log')
        timestamp = now()
        d0 = OrderedDict([("history",[(timestamp,"created")])])
        with open(filename,'w') as f:
            json.dump( d0, f, indent=2 ) 

    return d0

