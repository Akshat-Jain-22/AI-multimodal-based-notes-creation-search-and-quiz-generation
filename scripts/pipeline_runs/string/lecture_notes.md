# string

## Thevenin’s Theorem and Its Origin in Node‑Voltage Analysis  

The Thevenin theorem provides a powerful way to replace any linear, bilateral network that drives a load with a single voltage source \(V_{\text{th}}\) in series with a resistance \(R_{\text{th}}\).  Once this equivalent is known, the behaviour of the load resistor \(R_L\) can be analysed with a simple two‑element circuit, greatly simplifying design and troubleshooting.

### Why a Thevenin Equivalent Exists  

Consider a linear circuit that supplies a load resistor \(R_L\).  The quantity of interest is the voltage across \(R_L\), denoted \(V_{RL}\).  Because the network is linear, the relationship between \(V_{RL}\) and the circuit parameters (source values and element resistances) must be linear as well.  In other words, changing \(R_L\) will scale the load voltage proportionally, a hallmark of a voltage source in series with a resistor.

To see this concretely, we can write the node‑voltage equations for the original network.  Choose a reference node (ground) and assign node voltages \(V_1, V_2,\) and \(V_3\) to the remaining nodes A, B, and C, respectively.  With the reference node fixed at 0 V, each branch current can be expressed in terms of the voltage differences across its endpoints.  Introducing conductances  
\[
G_1=\frac{1}{R_1},\qquad G_2=\frac{1}{R_2},\quad\text{etc.},
\]
the current leaving node A through resistor \(R_1\) is simply  
\[
I_{A\to C}=G_1\,(V_1-V_3).
\]

Applying Kirchhoff’s Current Law (KCL) at node A (and similarly at nodes B and C) yields a set of linear equations in the unknown node voltages.  Solving these equations gives \(V_1, V_2, V_3\) as linear functions of the independent sources and of the load resistance \(R_L\).  Because the solution is linear, the voltage across the load can be written in the form  
\[
V_{RL}=V_{\text{th}}-\;I_{L}\,R_{\text{th}},
\]
where \(I_{L}=V_{RL}/R_L\) is the load current.  Rearranging gives the familiar Thevenin representation: a single source \(V_{\text{th}}\) driving \(R_L\) through a series resistance \(R_{\text{th}}\).

### Extracting the Thevenin Parameters  

1. **Thevenin Voltage (\(V_{\text{th}}\))**  
   - Remove the load resistor \(R_L\) (open‑circuit the terminals).  
   - The voltage that appears across the open terminals is exactly \(V_{\text{th}}\).  
   - In the node‑voltage picture this corresponds to solving the KCL equations with the branch containing \(R_L\) omitted, yielding the open‑circuit node voltage at the load terminals.

2. **Thevenin Resistance (\(R_{\text{th}}\))**  
   - One common method is to deactivate all independent sources (replace voltage sources with short circuits and current sources with open circuits).  
   - With the sources turned off, the resistance seen looking into the terminals (with the load still removed) is \(R_{\text{th}}\).  
   - Alternatively, compute the short‑circuit current \(I_{\text{sc}}\) that would flow if the load terminals were connected directly together; then \(R_{\text{th}} = V_{\text{th}} / I_{\text{sc}}\).

Because the conductance notation simplifies the algebra, the KCL at node A can be written compactly as  
\[
G_1\,(V_1-V_3) + \text{(other currents leaving A)} = 0,
\]
and analogous expressions hold for nodes B and C.  Solving the resulting linear system provides the open‑circuit voltage and the short‑circuit current needed for the Thevenin parameters.

### Graphical Extraction (Preview)  

Beyond algebraic calculation, the Thevenin voltage and resistance can be read directly from the circuit’s load‑voltage versus load‑current characteristic.  Plotting \(V_{RL}\) against \(I_{L}\) yields a straight line; the intercept on the voltage axis is \(V_{\text{th}}\), while the negative reciprocal of the slope gives \(R_{\text{th}}\).  This graphical method offers a quick sanity check and is especially useful when measurements are taken on a physical prototype.

### Summary  

The Thevenin theorem rests on the linearity of ordinary electric networks.  By expressing the network in terms of node voltages and conductances, KCL produces a set of linear equations whose solution reveals a simple equivalent: a voltage source \(V_{\text{th}}\) in series with a resistance \(R_{\text{th}}\).  Determining these two quantities—either analytically via open‑circuit and short‑circuit conditions or graphically from measured load behaviour—allows any complex linear circuit to be reduced to a form that is trivial to analyse for any attached load.