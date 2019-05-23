from qiskit import BasicAer
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import execute
from qiskit import IBMQ
import numpy as np
import matplotlib.pyplot as plt
from tqdm import trange

from qiskit.tools.monitor import job_monitor

# Insert your IBM token here
token = ''
IBMQ.enable_account(token)

num_qubits = 32

num_runs = 10

key_lengths = [] 
for _ in trange(num_runs):

    alice_state = np.random.randint(2, size=num_qubits)
    bob_basis = np.random.randint(2, size=num_qubits)
    eve_basis = np.random.randint(2, size=num_qubits)

    # print(alice_state)
    # print(bob_basis)
    # print(eve_basis)

    q = QuantumRegister(num_qubits,'q')
    c_bob = ClassicalRegister(num_qubits,'c_bob')
    c_eve = ClassicalRegister(num_qubits,'c_eve')

    b92 = QuantumCircuit(q,c_bob,c_eve,name='b92')

    # Alice prepares her qubits
    for index, _ in enumerate(alice_state):
        if alice_state[index] == 1:
            b92.h(q[index])
    b92.barrier() 

    # Eve chooses her bases
    for index, _ in enumerate(eve_basis):
        if eve_basis[index] == 0:
            b92.h(q[index])
    b92.barrier()  

    # Eve measures the qubits
    for index, _ in enumerate(eve_basis):
        b92.measure(q[index],c_eve[index])
    b92.barrier()        

    # Bob chooses his bases
    for index, _ in enumerate(bob_basis):
        if bob_basis[index] == 0:
            b92.h(q[index])
    b92.barrier()        
    
    # Bob measures the received qubits
    for index, _ in enumerate(bob_basis):        
        b92.measure(q[index],c_bob[index])          
    b92.barrier()       

    # backend = BasicAer.get_backend('qasm_simulator')
    # backend = IBMQ.get_backend('ibmq_16_melbourne')
    backend = IBMQ.get_backend('ibmq_qasm_simulator')

    num_shots = 8192 # Change this to alter the number of times your circuit runs

    job = execute(b92,backend,shots=num_shots)

    # job_monitor(job)

    result = job.result()
    counts = result.get_counts()


    bob_keys_temp = []
    eve_keys_temp = []


    # print("Bob's string\t\tEve's string")
    for count in [*counts]:
        bob_key = count[2*num_qubits:num_qubits-1:-1]
        eve_key = count[num_qubits::-1]
        bob_keys_temp.append(bob_key)
        eve_keys_temp.append(eve_key)
    #     print(bob_key + '\t' + eve_key)
    
    alice_keys = []
    eve_keys = []
    bob_keys = []
    for eve_temp_key, bob_temp_key in zip(eve_keys_temp,bob_keys_temp):
        alice_key = ''
        eve_key = ''
        bob_key = ''
        for i in range(num_qubits):
            if bob_temp_key[i] == '1': # Only choose bits where Bob measured a 1
                alice_key += str(alice_state[i])
                eve_key += str(eve_basis[i])
                bob_key += str(bob_basis[i])
        eve_keys.append(eve_key)
        bob_keys.append(bob_key)
        alice_keys.append(alice_key)

    alice_keys = []
    eve_keys = []
    bob_keys = []
    for eve_temp_key, bob_temp_key in zip(eve_keys_temp,bob_keys_temp):
        alice_key = ''
        eve_key = ''
        bob_key = ''
        for i in range(num_qubits):
            if bob_temp_key[i] == '1': # Only choose bits where Bob measured a 1
                alice_key += str(alice_state[i])
                eve_key += str(eve_basis[i])
                bob_key += str(bob_basis[i])
        eve_keys.append(eve_key)
        bob_keys.append(bob_key)
        alice_keys.append(alice_key)

    key_lengths += [len(key) for key in alice_keys]

print(np.mean(key_lengths)/num_qubits)
plt.hist(key_lengths,bins=np.arange(-0.5,num_qubits+0.5),ec='k')
plt.show()