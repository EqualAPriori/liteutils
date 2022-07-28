from pymbar import timeseries
import numpy as np
#from . import log

def stats(data,col=None,nskip=1):
    """
    Args:
        data (array,str): [Ndata x Nfields], or [Ndata,], or str to 2D data
        col (list,tuple): specific column to calculate for. if None, calculate for all.
        nskip (int): stride for trying time origins.
    Note:
        expect each column to be its own variable.
    """
    if isinstance(data,str):
        data = np.loadtxt(data)
        print(data)

    results = []
    if col is not None:
        data = data[:,col]

    if len(data.shape) == 1:
        results = stats_1d(data,nskip)
    else:
        print("here")
        ncols = data.shape[1]
        results = []
        for c in range(ncols):
            result = stats_1d(data[:,c],nskip)
            results.append(result) 
    
    return results

def stats_1d(data,nskip=1):
    """
    Args:
        data: 1D data
        nskip: stride for trying time origins.

    Returns:
    """

    # detect equlibration
    t0, g, Neff = timeseries.detect_equilibration(data, nskip=nskip)
    data_eq = data[t0:]
    indices = timeseries.subsample_correlated_data(data_eq, g=g)
    data_sampled = data_eq[indices]

    # statistics
    avg = data_sampled.mean()
    std = data_sampled.std()
    err = data_sampled.std()/np.sqrt( len(indices) )

    # output
    summary = [avg,std,err,t0,g,Neff]
    return summary
    
def format_stats(avg,std,err,t0=None,g=None,Neff=None,varname=None):
    """Pretty print statistics"""
    stats = "Statistics"
    if varname is not None:
        stats += " for {}".format(varname)
    stats += ":"

    stats += f"\n\tmean:\t\t\t\t{avg}\t+/-{err}"
    stats += f"\n\tstdev:\t\t\t\t{std}"
    if t0 is not None:
        stats += f"\n\tequilibration time:\t{t0}"
    if g is not None:
        stats += f"\n\tinefficiency:\t\t{g}"
    if Neff is not None:
        stats += f"\n\teffective samples:\t{Neff}"
        
    print(stats)
    return stats

# Add commandline access, maybe via entrypoint?

