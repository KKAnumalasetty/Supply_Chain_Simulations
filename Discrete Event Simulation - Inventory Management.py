#!/usr/bin/env python
# coding: utf-8

# In[12]:


# !pip install simpy
import simpy
print('simpy version: ',simpy.__version__)
import numpy as np
print('numpy version: ',np.__version__)

from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"


# # Setup Simpy environment
# ## Setting simulation to run for 5 days initially

# In[13]:


# env = simpy.Environment()
# env


# ## Define warehouse run event
# ### Takes order cutoff inventory level as an input-1
# ### Takes order target inventory level as an input-2

# In[14]:


def warehouse_run(env,order_cutoff, order_target):
    global inventory_level,profit,units_ordered
    
    inventory_level = order_target
    profit = 0.0
    units_ordered = 0
    
    #we need an infinite loop
    while True:
        customer_arrival = generate_customer_arrival()
        yield env.timeout(customer_arrival) #wait for the time interval for customer arrival
        profit -= inventory_level*2*customer_arrival
        
        demand = generate_customer_demand()
        #branch-1 : if demand is smaller than inventory, then we can sell complete amount
        if demand < inventory_level:
            profit +=100*demand
            inventory_level -= demand
            print('on {:.2f} day we sold {} and remaining inventory {}'.format(env.now,demand,inventory_level))
        #branch-2: if demand is more than inventory, then sell whatever portion of demand we can satisfy
        else:
            profit += 100*inventory_level
            inventory_level = 0
            print('on {:.2f} day we sold {} (out of stock)'.format(env.now,inventory_level))
    
        if inventory_level < order_cutoff and units_ordered == 0:
            #our inventory levels are below organization's policy level and there are no new orders placed, 
            #in such scenario we need to place an order
            env.process(handle_order(env,order_target))


#process generators
def generate_customer_arrival():
    return np.random.exponential(1.0/5)

#process generators
def generate_customer_demand():
    return np.random.randint(1,5)

def handle_order(env,order_target):
    global inventory_level,profit,units_ordered
    
    
    units_ordered = order_target -inventory_level
    print('on {:.2f} day we placed an order for {}'.format(env.now,units_ordered))
    profit -= 50*units_ordered
    yield env.timeout(2.0)
    inventory_level += units_ordered
    print('on {:.2f} day we received an order for {} and inventory level = {}'.format(env.now,units_ordered,inventory_level))
    units_ordered = 0


# ## Attaching process generators to Simpy environment - This step enables to run simulations later

# In[15]:


def observe(env,observation_time,inventory_level_list):
    global inventory_level
    
    while True:
        observation_time.append(env.now)
        inventory_level_list.append(inventory_level)
        yield env.timeout(0.1) #we will get 10 observations per day

        
observation_time = []
inventory_level_list = []

env = simpy.Environment()
env.process(warehouse_run(env,10,30))
env.process(observe(env,observation_time,inventory_level_list))
env


# ## Simulating for 5 days
# ### Before starting simulation, always set random seed to a specific number for reproducing the same results

# In[16]:


np.random.seed(0)
env.run(until=5.0)


# ## Visualization - Where simulations come to life

# In[17]:


import matplotlib.pyplot as plt
import pandas as pd

inventory_DF = pd.DataFrame({
                            'Time':observation_time,
                            'Inventory_Level':inventory_level_list
})

inventory_DF.style

plt.figure()
plt.step(observation_time,inventory_level_list,where='post')
plt.xlabel('Simulation Time (days)')
plt.ylabel('Inventory level (units)')

print('profit = ${:0,.2f}'.format(profit))


# In[18]:


# inventory_DF.plot()

def run_simulation(days,cutoff,target):
    observation_time = []
    inventory_level_list = []
    env = simpy.Environment()
    env.process(warehouse_run(env,cutoff,target))
    env.process(observe(env,observation_time,inventory_level_list))
    env.run(until=days)
    inventory_DF = pd.DataFrame({
                            'Time':observation_time,
                            'Inventory_Level':inventory_level_list
    })
    return inventory_DF


# # Simulate for 5 days with different cutoff and target levels

# In[19]:


inventory_DF = run_simulation(5,50,100)
inventory_DF.plot(x='Time', y='Inventory_Level',style='.-')


# In[20]:


get_ipython().system('pip install panel')


# In[21]:


import panel as pn
pn.extension()

def plot_sim_result(inventory_DF):
    import matplotlib
    matplotlib.rcParams.update({'font.size': 22})
    fig = inventory_DF.plot(x='Time', y='Inventory_Level',style='.-',ylim=(0,100),figsize=(10,6)).get_figure()
    ax =fig.axes
    ax[0].set_xlabel("Simulation Time (in Days)")
    ax[0].set_ylabel("Inventory Level (in Units)")
    fig.suptitle('Simulating Inventory levels')
#     fig = plt.figure()
#     plt.step(observation_time,inventory_level_list,where='post')
#     plt.xlabel('Simulation Time (days)')
#     plt.ylabel('Inventory level (units)')
    plt.close(fig)
    return fig


# pn.widgets.Player(name='Discrete Player', start=0, end=100, value=32, loop_policy='loop')
# days=pn.widgets.IntSlider(name='Days',start=1,end=365,step=1,value=5)

def run_simulation_demo(days=pn.widgets.Player(name='Days to Simulate', start=1, end=10, value=5, loop_policy='loop'),
                        cutoff=pn.widgets.IntSlider(name='Cutoff Inventory',start=1,end=100,step=1,value=10),
                        target=pn.widgets.IntSlider(name= 'Target Inventory',start=1,end=100,step=1,value=30),
                        view_fn=plot_sim_result):
    observation_time = []
    inventory_level_list = []
    env = simpy.Environment()
    env.process(warehouse_run(env,cutoff,target))
    env.process(observe(env,observation_time,inventory_level_list))
    env.run(until=days)
    inventory_DF = pd.DataFrame({
                            'Time':observation_time,
                            'Inventory_Level':inventory_level_list
    })
    return view_fn(inventory_DF)


# In[23]:


pn.interact(run_simulation_demo).show()

