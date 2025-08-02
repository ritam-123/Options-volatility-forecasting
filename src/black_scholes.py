import math
from scipy.stats import norm

def black_scholes_puts(S,K,T,r,sigma):
    d1=(math.log(S/K)+(r+(sigma*sigma)/2)*T)/(sigma*math.sqrt(T))
    d2=d1-sigma*math.sqrt(T)

    put_price=K*math.exp(-r*T) * norm.cdf(-d2)- S*(norm.cdf(-d1))

    return put_price


def black_scholes_calls(S,K,T,r,sigma):
    d1=(math.log(S/K)+(r+(sigma*sigma)/2)*T)/(sigma*math.sqrt(T))
    d2=d1-sigma*math.sqrt(T)
    call_price=S*norm.cdf(d1)-K*math.exp(-r*T)*norm.cdf(d2)

    return call_price