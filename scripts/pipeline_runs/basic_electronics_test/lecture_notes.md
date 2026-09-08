# Basic Electronics Test

## Thevenin’s Theorem – From Circuit Description to an Equivalent Source  

In order to simplify the analysis of linear circuits that feed a particular load, it is often convenient to replace the whole network (everything except the load) with a single voltage source in series with a single resistance.  This replacement is the **Thevenin equivalent** of the original circuit.  The theorem guarantees that, as far as the load is concerned, the original network and its Thevenin equivalent produce exactly the same voltage‑current relationship.

### Why a circuit can be represented by a Thevenin source  

Consider a linear network that is connected to a load resistor \(R_L\).  The quantity of interest is the voltage \(V\) that appears across \(R_L\).  Because the network is linear, the relationship between the load current \(I_L\) and the load voltage \(V\) must be linear; it can be expressed in the form  

\[
V = V_{\text{th}} - I_L R_{\text{th}},
\]

where \(V_{\text{th}}\) is the open‑circuit voltage at the load terminals (the voltage that would be measured if \(R_L\) were removed) and \(R_{\text{th}}\) is the resistance that the network presents to the load when all independent sources are turned off.  This linear expression is precisely the behavior of a single ideal voltage source \(V_{\text{th}}\) in series with a resistor \(R_{\text{th}}\).  Hence any linear two‑terminal network can be replaced by that simple pair without altering the external voltage‑current characteristics.

### Determining the Thevenin parameters graphically and analytically  

#### 1. Choose a reference node  
Select a node in the circuit to serve as the ground (reference) point.  Its voltage is defined as \(0\; \text{V}\).  In the example shown in the lecture, the bottom node was taken as the reference.

#### 2. Assign node voltages  
Label the potentials of the remaining nodes with respect to the reference node:
- Node A: \(V_1\)  
- Node B: \(V_2\)  
- Node C: \(V_3\)

#### 3. Write KCL equations in terms of conductances  
It is often algebraically convenient to work with **conductances**, defined as the reciprocal of resistance:

\[
G_1 = \frac{1}{R_1},\qquad 
G_2 = \frac{1}{R_2},\qquad 
G_3 = \frac{1}{R_3},\; \text{etc.}
\]

For each node, apply Kirchhoff’s Current Law (the algebraic sum of currents leaving the node is zero).  Taking currents that leave the node as positive, the KCL at node A becomes  

\[
G_1\,(V_1 - V_3) + G_2\,(V_1 - V_2) + G_3\,V_1 = 0,
\]

where the three terms correspond respectively to the currents through \(R_1\), \(R_2\) and any resistor that connects node A directly to ground.

Similar equations are written for nodes B and C, each expressed solely in terms of the node voltages and the conductances that connect the nodes.

#### 4. Solve for the node voltages  
The set of linear equations obtained in the previous step can be solved (by substitution, matrix methods, or graphically) to obtain the values of \(V_1\), \(V_2\) and \(V_3\).  Once these are known, the voltage across the load resistor \(R_L\) is simply the difference between the node potentials that the load connects—typically \(V = V_{\text{node at one end}} - V_{\text{node at the other end}}\).

#### 5. Extract the Thevenin voltage \(V_{\text{th}}\)  
The **Thevenin voltage** is the open‑circuit voltage at the load terminals.  In practice, set \(R_L\) to infinity (i.e., remove the load) and recompute the node voltages.  The voltage appearing across the open terminals is \(V_{\text{th}}\).

#### 6. Extract the Thevenin resistance \(R_{\text{th}}\)  
Two equivalent methods are common:

* **Zero‑source method** – Turn off every independent source (replace voltage sources with short circuits and current sources with open circuits).  Then compute the equivalent resistance seen looking into the load terminals; this resistance is \(R_{\text{th}}\).

* **Slope method** – Vary the load resistance, plot the resulting load voltage \(V\) versus the load current \(I_L\), and determine the slope of the straight line.  The negative of that slope equals \(R_{\text{th}}\).

Both procedures yield the same numerical value for the Thevenin resistance.

### Example: Finding the voltage across a load resistor  

The lecture illustrated the procedure with a specific circuit that contained three resistors \(R_1, R_2, R_3\) and a load resistor \(R_L\) connected between nodes B and C.  After designating the ground node, the node voltages \(V_1, V_2, V_3\) were introduced.  Conductances \(G_1 = 1/R_1\), \(G_2 = 1/R_2\), etc., were defined, and KCL equations were written.  For node A the current expression was highlighted:

\[
\text{Current leaving A through } R_1 = \frac{V_1 - V_3}{R_1} = G_1 (V_1 - V_3).
\]

By solving the full system, the voltage across the load, \(V_{RL}\), could be expressed directly in terms of the original resistances and any independent source values.  Once that expression was obtained, the same circuit was reduced to its Thevenin form: a single source \(V_{\text{th}}\) in series with a

**Diagrams/board content from this segment:**

![~ NPTEL (captured at 5.0s)](extracted_images/test_short/frame_5.0s.png)
*~ NPTEL (captured at 5.0s)*

![BASIC ELECTRONICS mst - (captured at 10.0s)](extracted_images/test_short/frame_10.0s.png)
*BASIC ELECTRONICS mst - (captured at 10.0s)*

![The, Re Oe R ‘ oN How is V related tothe circuit parameters? (captured at 60.0s)](extracted_images/test_short/frame_60.0s.png)
*The, Re Oe R ‘ oN How is V related tothe circuit parameters? (captured at 60.0s)*
