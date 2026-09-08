# string  

*In this chapter we explore Thevenin’s theorem from the perspective of node‑voltage analysis.  Starting with the linear algebra that underlies any bilateral network, we derive the existence of a Thevenin equivalent, show how to obtain its voltage $V_{\text{th}}$ and resistance $R_{\text{th}}$ analytically, and illustrate a graphical method for extracting the same parameters from measured load‑characteristics.*  

## Thevenin’s Theorem and Its Origin in Node‑Voltage Analysis  

The Thevenin theorem states that any linear, bilateral network driving a load can be replaced by a single voltage source $V_{\text{th}}$ in series with a resistance $R_{\text{th}}$.  Once this equivalent is known, the behaviour of the load resistor $R_L$ is described by a simple two‑element circuit, greatly simplifying design, analysis, and troubleshooting.

### Why a Thevenin Equivalent Exists  

Consider a linear circuit that supplies a load resistor $R_L$.  The quantity of interest is the voltage across the load, denoted $V_{RL}$.  Because the network is linear, the relationship between $V_{RL}$ and the circuit parameters (source values and element resistances) must also be linear.  Consequently, changing $R_L$ scales the load voltage proportionally—a hallmark of a voltage source in series with a resistor.

To see this concretely, we write the node‑voltage equations for the original network.  Choose a reference node (ground) and assign node voltages $V_1$, $V_2$, and $V_3$ to the remaining nodes A, B, and C, respectively.  With the reference node fixed at $0\;\text{V}$, each branch current can be expressed in terms of the voltage differences across its endpoints.  Introducing conductances  

$$
G_1 = \frac{1}{R_1}, \qquad
G_2 = \frac{1}{R_2}, \qquad \text{etc.}
$$  

the current leaving node A through resistor $R_1$ is simply  

$$
I_{A\to C}= G_1\,(V_1 - V_3).
$$  

Applying Kirchhoff’s Current Law (KCL) at node A (and similarly at nodes B and C) yields a set of linear equations in the unknown node voltages.  Solving these equations provides $V_1$, $V_2$, and $V_3$ as linear functions of the independent sources and of the load resistance $R_L$.  Because the solution is linear, the voltage across the load can be written in the form  

$$
V_{RL}= V_{\text{th}} - I_{L}\,R_{\text{th}},
$$  

where $I_{L}=V_{RL}/R_L$ is the load current.  Rearranging gives the familiar Thevenin representation: a single source $V_{\text{th}}$ driving $R_L$ through a series resistance $R_{\text{th}}$.

### Determining the Thevenin Parameters  

#### Thevenin Voltage $V_{\text{th}}$  

1. Remove the load resistor $R_L$ (open‑circuit the terminals).  
2. Solve the node‑voltage equations with the branch containing $R_L$ omitted.  
3. The resulting open‑circuit voltage across the terminals is $V_{\text{th}}$.

#### Thevenin Resistance $R_{\text{th}}$  

Two common approaches are equivalent:

* **Source‑deactivation method** – Replace every independent voltage source by a short circuit and every independent current source by an open circuit.  With the load still removed, compute the resistance seen looking into the terminals; this resistance is $R_{\text{th}}$.

* **Short‑circuit method** – Re‑insert the load terminals and force them together (short circuit).  Determine the short‑circuit current $I_{\text{sc}}$ that would flow.  Then  

$$
R_{\text{th}} = \frac{V_{\text{th}}}{I_{\text{sc}}}.
$$  

Because the conductance notation simplifies the algebra, the KCL at node A can be written compactly as  

$$
G_1\,(V_1 - V_3) + \text{(other currents leaving A)} = 0,
$$  

with analogous expressions for nodes B and C.  Solving the resulting linear system provides both the open‑circuit voltage $V_{\text{th}}$ and the short‑circuit current $I_{\text{sc}}$ required for the Thevenin parameters.

### Graphical Extraction of Thevenin Parameters  

The Thevenin voltage and resistance can also be obtained directly from the circuit’s load‑voltage versus load‑current characteristic.  Plotting $V_{RL}$ against $I_{L}$ yields a straight line; the intercept on the voltage axis equals $V_{\text{th}}$, while the negative reciprocal of the slope gives $R_{\text{th}}$.  This graphical method offers a quick sanity check and is especially useful when measurements are taken on a physical prototype.

### Summary  

The Thevenin theorem rests on the linearity of ordinary electric networks.  By expressing the network in terms of node voltages and conductances, KCL produces a set of linear equations whose solution reveals a simple equivalent: a voltage source $V_{\text{th}}$ in series with a resistance $R_{\text{th}}$.  Determining these two quantities—either analytically via open‑circuit and short‑circuit conditions or graphically from measured load behaviour—allows any complex linear circuit to be reduced to a form that is trivial to analyse for any attached load.

---

**Key Takeaways**

- Any linear, bilateral network can be replaced by a Thevenin equivalent $V_{\text{th}}$ in series with $R_{\text{th}}$.  
- $V_{\text{th}}$ is the open‑circuit voltage at the load terminals; $R_{\text{th}}$ can be found by deactivating sources or by $R_{\text{th}} = V_{\text{th}}/I_{\text{sc}}$.  
- Node‑voltage analysis, expressed with conductances, provides a systematic way to derive the Thevenin parameters algebraically.  
- A plot of load voltage versus load current yields $V_{\text{th}}$ (voltage intercept) and $R_{\text{th}}$ (negative reciprocal of the slope) graphically.  
- Reducing a complex circuit to its Thevenin form simplifies analysis, design, and troubleshooting for any connected load.