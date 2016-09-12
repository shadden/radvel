import numpy as np        
import copy
import pandas as pd
from orbit import timeperi_to_timetrans, timetrans_to_timeperi

# List of available bases
BASIS_NAMES = [
'per tp e w k', # The CPS basis
'per tc secosw sesinw logk',
'per tc secosw sesinw k',
'per tc e w k'

]
    
def _print_valid_basis():
    print "Available bases:"
    print "\n".join(BASIS_NAMES)

class Basis(object):
    """
    Object that knows how to convert between the various Keplerian bases

    Args:
        name (str): basis name
        num_planets (int): number of planets

    Attributes:
        cps_params (str): name of CPS basis

    Note:
        Valid basis functions: \n
        'per tp e w k' (The CPS basis) \n
        'per tc secosw sesinw logk'  \n 
        'per tc secosw sesinw k'  \n
        'per tc e w k'
    """
    
    cps_params = 'per tp e w k'.split()
    def __init__(self, *args):
        self.name = None
        self.num_planets = 0
        if len(args)==0:
            _print_valid_basis()
            return None
        
        name, num_planets = args

        if BASIS_NAMES.count(name)==0:
            print "{} not valid basis".format(name)
            _print_valid_basis()
            return None

        self.name = name
        self.num_planets = num_planets
        self.params = name.split()

    def __repr__(self):
        return "Basis Object <{}>".format(self.name)

        
    def to_cps(self, params_in, **kwargs):
        """Convert to CPS basis

        Convert a dictionary with parameters of a given basis into the
        cps basis

        Args:
            params_in (dict): planet parameters expressed in current basis

        Returns: 
            dict or DataFrame: parameters expressed in the CPS basis

        """

        params_out = copy.copy(params_in)
        for num_planet in range(1,1+self.num_planets):
            def _getpar(key):
                return params_out['{}{}'.format(key,num_planet)]
            def _setpar(key, value):
                params_out['{}{}'.format(key,num_planet)] = value
            def _delpar(key):
                if isinstance(params_in,dict):
                    del params_out['{}{}'.format(key,num_planet)]
                elif isinstance(params_in,pd.core.frame.DataFrame):
                    params_out.drop('{}{}'.format(key,num_planet))

            # transform into CPS basis
            if self.name == 'per tp e w k':
                # already in the CPS basis
                per = _getpar('per')
                tp = _getpar('tp')
                e = _getpar('e')
                w = _getpar('w')
                k = _getpar('k')
                
            if self.name == 'per tc e w k':
                per = _getpar('per')
                tc = _getpar('tc')
                e = _getpar('e')
                w = _getpar('w')
                k = _getpar('k')
                tp = timetrans_to_timeperi(tc, per, e, w)
            
            if self.name=='per tc secosw sesinw logk':
                # pull out parameters
                per = _getpar('per')
                tc = _getpar('tc')
                secosw = _getpar('secosw')
                sesinw = _getpar('sesinw')
                logk = _getpar('logk')

                k = np.exp(logk)
                e = secosw**2 + sesinw**2
                w = np.arctan2(sesinw , secosw)
                tp = timetrans_to_timeperi(tc, per, e, w)

            if self.name=='per tc secosw sesinw k':
                # pull out parameters
                per = _getpar('per')
                tc = _getpar('tc')
                secosw = _getpar('secosw')
                sesinw = _getpar('sesinw')
                k = _getpar('k')
            
                # transform into CPS basis
                e = secosw**2 + sesinw**2
                w = np.arctan2(sesinw , secosw)
                tp = timetrans_to_timeperi(tc, per, e, w)

                                
            # shoves cps parameters from namespace into param_out
            _setpar('per', per)
            _setpar('tp', tp)
            _setpar('e', e)
            _setpar('w', np.degrees(w))
            _setpar('k', k)


        return params_out


    def from_cps(self, params_in, newbasis, **kwargs):
        """Convert from CPS basis into another basis

        Convert a dictionary with parameters of a given basis into the cps basis

        Args:
            params_in (dict):  planet parameters expressed in cps basis
            newbasis (string): string corresponding to basis to switch into
            keep (bool): (optional) If true keep the parameters expressed in the old basis,
                else remove them from the output dictionary/DataFrame

        Returns:
            Dictionary or dataframe with the parameters converted into the new basis

        """
        
        if newbasis not in BASIS_NAMES:
            print "{} not valid basis".format(newbasis)
            _print_valid_basis()
            return None
        
        params_out = copy.copy(params_in)
        for num_planet in range(1,1+self.num_planets):
            def _getpar(key):
                return params_out['{}{}'.format(key,num_planet)]
            def _setpar(key, value):
                params_out['{}{}'.format(key,num_planet)] = value
            def _delpar(key):
                if isinstance(params_in,dict):
                    del params_out['{}{}'.format(key,num_planet)]
                elif isinstance(params_in,pd.core.frame.DataFrame):
                    params_out.drop('{}{}'.format(key,num_planet))
            

            if newbasis == 'per tc e w k':
                pass
            
            if newbasis == 'per tc secosw sesinw logk':
                per = _getpar('per')
                e = _getpar('e')
                w = _getpar('w')
                k = _getpar('k')
                try:
                    tp = _getpar('tp')
                except KeyError:
                    tc = _getpar('tc')
                    tp = timetrans_to_timeperi(tc, per, e, w)
                    _setpar('tp', tp)
                    
                _setpar('secosw', np.sqrt(e)*np.cos(w) )
                _setpar('sesinw', np.sqrt(e)*np.sin(w) )
                _setpar('logk', np.log(k) )
                _setpar('tc', timeperi_to_timetrans(tp, per, e, w) )

                if not kwargs.get('keep', True):
                    _delpar('tp')
                    _delpar('e')
                    _delpar('w')
                    _delpar('k')

                self.name = newbasis
                self.params = newbasis.split()

                
            if newbasis == 'per tc secosw sesinw k':
                per = _getpar('per')
                e = _getpar('e')
                w = _getpar('w')
                k = _getpar('k')
                try:
                    tp = _getpar('tp')
                except KeyError:
                    tp = timetrans_to_timeperi(_getpar('tc'), per, e, w)
                    _setpar('tp', tp)
                    
                _setpar('secosw', np.sqrt(e)*np.cos(w) )
                _setpar('sesinw', np.sqrt(e)*np.sin(w) )
                _setpar('k', k )
                _setpar('tc', timeperi_to_timetrans(tp, per, e, w) )

                if not kwargs.get('keep', True):
                    _delpar('tp')
                    _delpar('e')
                    _delpar('w')

                self.name = newbasis
                self.params = newbasis.split()


        return params_out
                
