import numpy as np
from numba import jit

@jit(error_model='numpy')
def point_electrode_dipoles(csf_thick):
    h=0.001
    i0=1e-3
    rho1=0.5
    rho2=2.5
    K21=(rho2-rho1)/(rho2+rho1)
    scale=(i0*rho1)/(2*np.pi)
    x_offset=0
    z_offset=0

    ex = np.zeros((1001,1001))
    ez = np.zeros((1001,1001))
    cx1 = np.zeros((50,1))
    cx2 = np.zeros((50,1))
    cz1 = np.zeros((50,1))
    cz2 = np.zeros((50,1))
    Ex = np.zeros((1001,1001))
    Ez = np.zeros((1001,1001))
    lookx1 =np.zeros((1001,1001))
    lookx2 = np.zeros((1001,1001))
    lookz1 = np.zeros((1001,1001))
    lookz2 = np.zeros((1001,1001))
    cxb1 = np.zeros((50,1))
    czb1 = np.zeros((50,1))
    cxb2 = np.zeros((50,1))
    czb2 = np.zeros((50,1))

    Ex_minus =np.zeros((1001,1001))
    Ez_minus = np.zeros((1001,1001))

    for k in range(0,1001):
        x= np.float32(x_offset+(k)*0.00001)
        for j in range(0,csf_thick):
            #import pdb;pdb.set_trace()

            z=z_offset+(j)*0.00001
            #print(type(z))
            r=np.sqrt(x**2+z**2)

            Eox=x*scale/(x**2+z**2)**1.5
            Eoz=z*scale/(x**2+z**2)**1.5

            ex[j,k]=Eox
            ez[j,k]=Eoz

            n = np.arange(0,50)
            m = n-1
            cx1 = (x*K21**(n+1)/((2*(n+1)*h-z)**2+x**2)**1.5)
            cx2 =(x*K21**(n+1)/((2*(n+1)*h+z)**2+x**2)**1.5)
            cz1 = (-(2*(n+1)*h-z)*K21**(n+1)/((2*(n+1)*h-z)**2+x**2)**1.5)
            cz2 = ((2*(n+1)*h+z)*K21**(n+1)/((2*(n+1)*h+z)**2+x**2)**1.5)

            #
            # for n in range(0,50):
            #     m=n-1
            #     cx1[n,0]=(x*K21**(n+1)/((2*(n+1)*h-z)**2+x**2)**1.5)
            #     cx2[n,0]=(x*K21**(n+1)/((2*(n+1)*h+z)**2+x**2)**1.5)
            #     cz1[n,0]=(-(2*(n+1)*h-z)*K21**(n+1)/((2*(n+1)*h-z)**2+x**2)**1.5)
            #     cz2[n,0]=((2*(n+1)*h+z)*K21**(n+1)/((2*(n+1)*h+z)**2+x**2)**1.5)

            Cxo1=scale*np.sum(cx1)
            Cxo2=scale*np.sum(cx2)
            Czo1=scale*np.sum(cz1)
            Czo2=scale*np.sum(cz2)

            lookx1[j,k]=Cxo1
            lookx2[j,k]=Cxo2
            lookz1[j,k]=Czo1
            lookz2[j,k]=Czo2

            Ex[j,k]=Eox+Cxo1+Cxo2
            Ez[j,k]=Eoz+Czo1+Czo2


    for k in range(0,1001):
        x=np.float32(x_offset+(k)*0.00001)
        for j in range(csf_thick,1001):
            z=z_offset+(j)*0.00001
            r=np.sqrt(x**2+z**2)

            Eox=x*scale/(x**2+z**2)**1.5
            Eoz=z*scale/(x**2+z**2)**1.5

            ex[j,k]=Eox
            ez[j,k]=Eoz

            n = np.arange(0,50)
            m = n -0
            cxb1 = (x*K21**(n+1)/((2*m*h+z)**2+x**2)**-1.5)
            cxb2 = (x*K21**(n+1)/((2*(n+1)*h+z)**2+x**2)**-1.5)
            czb1 = ((2*m*h+z)*K21**(n+1)/((2*m*h+z)**2+x**2)**1.5)
            czb2 = ((2*(n+1)*h+z)*K21**(n+1)/((2*(n+1)*h+z)**2+x**2)**1.5)
            #
            # for n in range(0,50):
            #     m=n-0
            #     cxb1[n]=(x*K21**(n+1)/((2*m*h+z)**2+x**2)**-1.5)
            #     cxb2[n]=(x*K21**(n+1)/((2*(n+1)*h+z)**2+x**2)**-1.5)
            #     czb1[n]=((2*m*h+z)*K21**(n+1)/((2*m*h+z)**2+x**2)**1.5)
            #     czb2[n]=((2*(n+1)*h+z)*K21**(n+1)/((2*(n+1)*h+z)**2+x**2)**1.5)

            Cxob1=scale*np.sum(cxb1)
            Cxob2=scale*np.sum(cxb2)
            Czob1=scale*np.sum(czb1)
            Czob2=scale*np.sum(czb2)

            lookx1[j,k]=Cxob1
            lookx2[j,k]=Cxob2
            lookz1[j,k]=Czob1
            lookz2[j,k]=Czob2

            Ex[j,k]=Eox+Cxob1+Cxob2
            Ez[j,k]=Eoz+Czob1+Czob2

    for j in np.arange(0,1001):
        Ex_minus[:,1000-j]=Ex[:,j]
        Ez_minus[:,1000-j]=-Ez[:,j]

    E=np.sqrt((Ex+Ex_minus)**2+(Ez+Ez_minus)**2)
    return E
