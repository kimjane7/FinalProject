import numpy as np
from wavefunction import FeedForwardNeuralNetwork
from hamiltonian import CalogeroSutherland
from sampler import ImportanceSampling
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as cm
from matplotlib import rc

plt.rcParams["font.family"] = "serif"
plt.rcParams["mathtext.fontset"] = "dejavuserif"
mpl.rcParams['text.usetex'] = True
mpl.rcParams['text.latex.preamble'] = [r'\usepackage{amsmath}']


def smooth_avg(x, y, n):

    num_points = int(np.ceil(len(x)/float(n)))
    X = np.zeros(num_points)
    Y = np.zeros(num_points)
    
    for i in range(num_points-1):
        X[i] = x[int((0.5+i)*n)]
        Y[i] = y[i*n:(i+1)*n].mean()
    X[-1] = x[-1]
    Y[-1] = y[(num_points-1)*n:].mean()
    
    return X, Y
    
    
    
    


def plot_reinforcement_EL(N, M, samples, nu):

    file = 'data/reinforcement_N'+str(N)+'_M'+str(M)+'_samples'+str(samples)+'_nu'+str(nu)+'.txt'
    data = np.loadtxt(file)
    
    cycle = data[:,0]
    fidelity = data[:,1]
    EL = data[:,2]
    EL_var = data[:,3]
    
    X, Y = smooth_avg(cycle, EL, 200)
    
    plt.plot(X, Y)
    plt.show()
    
plot_reinforcement_EL(2, 20, 10000, 0.5)
    
    


def plot_supervised_snapshots_N1(M):

    file = 'states/supervised_N1_M'+str(M)+'.txt'
    statefile = open(file, 'r')
    snapshots = statefile.readlines()
    statefile.close()
    
    WaveFunction = FeedForwardNeuralNetwork(1, M)
    Hamiltonian = CalogeroSutherland(WaveFunction, 0.0, 0.0)
    
    plt.figure(figsize=(12,8))
    colors = cm.rainbow_r(np.linspace(0, 1, len(snapshots)))
    
    num_points = 200
    x = np.linspace(-5.0,5.0,num_points)
    
    for snapshot, color in zip(snapshots, colors):
        
        WaveFunction.alpha = np.array(snapshot.split()[1:]).astype(np.float)
        WaveFunction.separate()
        
        psi = np.zeros(num_points)
        for i in range(num_points):
            psi[i] = WaveFunction.calc_psi([x[i]])
            
        plt.plot(x, psi, color=color, linewidth=3, label=str(snapshot.split()[0])+' updates')
    
    psi_nonint = np.zeros(num_points)
    for i in range(num_points):
        psi_nonint[i] = Hamiltonian.nonint_gs_wavefunction([x[i]])
    plt.plot(x, psi_nonint, color='k', linewidth=2, linestyle='dashed', label=r'$\Psi_0^{non\text{-}int}(x)$')
    
    plt.ylim(-0.1,1.5)
    plt.xlim(-5,5)
    plt.ylabel(r'Ground state wave function $\Psi(x)$', fontsize=14)
    plt.xlabel(r'Position $x$', fontsize=14)
    plt.title(r'Supervised learning of the wave function for the non-interacting case', fontsize=16)
    plt.legend(loc='upper right', fontsize=14)
    plt.savefig('figures/N1_M'+str(M)+'_supervised_snapshots.png', format='png')
    
    
    

def plot_supervised_snapshots(N, M):
    
    if N == 1:
        plot_supervised_snapshots_N1(M)
        
    else:
        file = 'states/supervised_N'+str(N)+'_M'+str(M)+'.txt'
        statefile = open(file, 'r')
        snapshots = statefile.readlines()
        statefile.close()
        
        WaveFunction = FeedForwardNeuralNetwork(N, M)
        Hamiltonian = CalogeroSutherland(WaveFunction, 0.0, 0.0)
        Sampler = ImportanceSampling(Hamiltonian, 0.005)
        
        plt.figure(figsize=(12,8))
        sns.set_style("whitegrid")
        colors = cm.rainbow_r(np.linspace(0, 1, len(snapshots)))
        num_samples = 300000
        num_skip = 3000
    
        index = [0, 3, 4, 5, 7, 9, 13]
        for snapshot, color in zip([snapshots[i] for i in index], [colors[i] for i in index]):
            
            WaveFunction.alpha = np.array(snapshot.split()[1:]).astype(np.float)
            WaveFunction.separate()
            WaveFunction.x = np.random.normal(0, 1/np.sqrt(2), N)
            
            for sample in range(num_skip):
                accepted = Sampler.sample()
                
            x = np.empty(N*num_samples)
            for sample in range(num_samples):
                accepted = Sampler.sample()
                x[N*sample:N*(sample+1)] = WaveFunction.x
                
            sns.kdeplot(x, shade=True, linewidth=2, color=color, label=str(snapshot.split()[0])+' updates')
        
        
        x = np.random.normal(0, 1/np.sqrt(2), N*num_samples)
        sns.kdeplot(x, shade=False, linewidth=3, color='k', linestyle='dashed', label=r'$|\Psi_0^{non\text{-}int}(x)|^2$')
        

        plt.ylim(-0.1,0.7)
        plt.xlim(-4,4)
        plt.ylabel(r'Probability distribution $|\Psi(x)|^2$', fontsize=14)
        plt.xlabel(r'Positions $x$', fontsize=14)
        plt.title('Supervised learning of the wave function for the non-interacting case', fontsize=16)
        plt.legend(loc='upper right')
        plt.savefig('figures/N'+str(N)+'_M'+str(M)+'_supervised_snapshots.png', format='png')


