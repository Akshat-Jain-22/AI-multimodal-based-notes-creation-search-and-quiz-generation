# Basic Electronics Test  

**Introduction**  
This chapter presents a comprehensive treatment of Thevenin’s theorem, a powerful tool for simplifying linear circuits that drive a particular load.  We first explain why any linear two‑terminal network can be represented by an equivalent voltage source and series resistance, then describe systematic methods—both graphical and analytical—for obtaining the Thevenin voltage and resistance.  An illustrative example ties the theory to practice, showing how node‑voltage analysis leads directly to the Thevenin equivalent.

## Thevenin’s Theorem: Replacing a Network by an Equivalent Source  

When a linear network supplies a load resistor \(R_{L}\), the quantity of interest is the voltage \(V\) that appears across the load.  Because the network is linear, the relationship between the load current \(I_{L}\) and the load voltage \(V\) must be linear and can be written as  

$$
V = V_{\text{th}} - I_{L}\,R_{\text{th}} ,
$$  

where  

* \(V_{\text{th}}\) is the **open‑circuit voltage** at the load terminals (the voltage measured when \(R_{L}\) is removed), and  
* \(R_{\text{th}}\) is the **Thevenin resistance**, i.e., the resistance presented to the load when all independent sources are turned off.

This expression is exactly the behavior of an ideal voltage source \(V_{\text{th}}\) in series with a resistor \(R_{\text{th}}\).  Consequently, any linear two‑terminal network can be replaced by that simple pair without altering the external voltage–current characteristics seen by the load.

## Determining Thevenin Parameters  

The following procedure outlines how to obtain \(V_{\text{th}}\) and \(R_{\text{th}}\) for a given circuit.

### 1. Choose a Reference Node  

Select one node to serve as the ground (reference) point; its voltage is defined as \(0\;\text{V}\).  In the lecture example, the bottom node was used as the reference.

### 2. Assign Node Voltages  

Label the potentials of the remaining nodes with respect to the reference node, for example  

* Node A: \(V_{1}\)  
* Node B: \(V_{2}\)  
* Node C: \(V_{3}\)

### 3. Write KCL Equations Using Conductances  

It is often algebraically convenient to work with **conductances**, the reciprocals of resistances:

$$
G_{1} = \frac{1}{R_{1}}, \qquad 
G_{2} = \frac{1}{R_{2}}, \qquad 
G_{3} = \frac{1}{R_{3}}, \; \text{etc.}
$$

Applying Kirchhoff’s Current Law (the algebraic sum of currents leaving a node equals zero) and taking currents that leave the node as positive, the KCL equation at node A becomes  

$$
G_{1}\,(V_{1}-V_{3}) + G_{2}\,(V_{1}-V_{2}) + G_{3}\,V_{1}=0 .
$$  

Similar equations are written for nodes B and C, each expressed solely in terms of node voltages and the conductances that connect the nodes.

### 4. Solve for the Node Voltages  

The resulting system of linear equations can be solved by substitution, matrix methods, or graphically to obtain the numerical values of \(V_{1}, V_{2}, V_{3}\).  Once the node voltages are known, the voltage across the load resistor is simply the difference between the potentials at the two terminals it connects:

$$
V_{RL}= V_{\text{terminal 1}} - V_{\text{terminal 2}} .
$$

### 5. Extract the Thevenin Voltage \(V_{\text{th}}\)  

The **Thevenin voltage** is the open‑circuit voltage at the load terminals.  Practically, remove the load (set \(R_{L}\to\infty\)) and recompute the node voltages.  The resulting voltage across the now‑open terminals is \(V_{\text{th}}\).

### 6. Extract the Thevenin Resistance \(R_{\text{th}}\)  

Two equivalent methods are commonly employed:

* **Zero‑source method** – Deactivate every independent source (replace voltage sources with short circuits and current sources with open circuits).  Then compute the equivalent resistance seen looking into the load terminals; this resistance is \(R_{\text{th}}\).

* **Slope method** – Vary the value of the load resistance, plot the load voltage \(V\) versus the load current \(I_{L}\), and determine the slope of the resulting straight line.  The negative of that slope equals \(R_{\text{th}}\).

Both approaches yield the same numerical value for the Thevenin resistance.

## Example: Applying the Procedure to a Specific Circuit  

The lecture demonstrated the above steps on a circuit containing three resistors \(R_{1}, R_{2}, R_{3}\) and a load resistor \(R_{L}\) connected between nodes B and C.

1. **Ground selection** – The bottom node was taken as the reference.  
2. **Node labeling** – Node potentials were denoted \(V_{1}, V_{2}, V_{3}\).  
3. **Conductance definitions** – \(G_{1}=1/R_{1},\; G_{2}=1/R_{2},\; G_{3}=1/R_{3}\).  
4. **KCL at node A** – The current leaving node A through \(R_{1}\) was expressed as  

   $$ 
   \frac{V_{1}-V_{3}}{R_{1}} = G_{1}\,(V_{1}-V_{3}) .
   $$  

   Analogous equations were written for nodes B and C, producing a solvable linear system.  

5. **Solution** – Solving the system gave explicit expressions for \(V_{1}, V_{2}, V_{3}\) in terms of the original resistances and source values.  The load voltage \(V_{RL}\) followed directly from the difference of the appropriate node voltages.  

6. **Thevenin reduction** – Using the open‑circuit voltage (with \(R_{L}\) removed) provided \(V_{\text{th}}\).  The zero‑source method yielded \(R_{\text{th}}\).  The original network was therefore replaced by a single source \(V_{\text{th}}\) in series with \(R_{\text{th}}\), dramatically simplifying further analysis.

**Diagrams/board content from this segment:**  

![~ NPTEL (captured at 5.0s)](extracted_images/test_short/frame_5.0s.png)  
*~ NPTEL (captured at 5.0s)*  

![BASIC ELECTRONICS mst - (captured at 10.0s)](extracted_images/test_short/frame_10.0s.png)  
*BASIC ELECTRONICS mst - (captured at 10.0s)*  

![The, Re Oe R ‘ oN How is V related tothe circuit parameters? (captured at 60.0s)](extracted_images/test_short/frame_60.0s.png)  
*The, Re Oe R ‘ oN How is V related tothe circuit parameters? (captured at 60.0s)*  

---

## Key Takeaways  

- Any linear two‑terminal network can be represented by a **Thevenin equivalent**: a single voltage source \(V_{\text{th}}\) in series with a resistance \(R_{\text{th}}\).  
- \(V_{\text{th}}\) is the open‑circuit voltage at the load terminals; \(R_{\text{th}}\) is the resistance seen looking into the terminals with all independent sources turned off.  
- Node‑voltage analysis (using conductances) provides a systematic way to compute the required node potentials and thus the Thevenin parameters.  
- Two practical methods for finding \(R_{\text{th}}\) are the **zero‑source method** (deactivating sources) and the **slope method** (using the \(V\)‑\(I\) characteristic).  
- Reducing a complex network to its Thevenin form greatly simplifies calculations for varying load conditions.