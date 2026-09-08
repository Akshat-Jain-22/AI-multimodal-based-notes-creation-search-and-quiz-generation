# Thevenin Theorem

## Thevenin’s Theorem – From Circuit Representation to Equivalent Parameters  

The Thevenin theorem tells us that any linear, bilateral network seen from a pair of terminals can be replaced by a single voltage source \(V_{\text{Th}}\) in series with a resistance \(R_{\text{Th}}\). This equivalent model reproduces exactly the voltage‑current relationship at the terminals, no matter what load is connected. Before we can state the theorem formally, we first examine **why** a circuit can be reduced in this way, and then we learn how to extract the two required parameters.

### 1. From a Complex Network to Node‑Voltage Equations  

Consider the circuit shown below (a load resistor \(R_L\) is attached across two terminals). To analyse the voltage across \(R_L\) we assign node voltages with respect to a reference node (ground).  

- Node A: voltage \(V_1\)  
- Node B: voltage \(V_2\) (the node directly connected to the load)  
- Node C: voltage \(V_3\)  

The reference node is chosen at the bottom of the schematic and is defined to be 0 V.  

#### Conductance notation  
It is convenient to work with conductances rather than resistances:

\[
G_1 = \frac{1}{R_1}, \qquad 
G_2 = \frac{1}{R_2}, \qquad 
\ldots
\]

Using conductances simplifies the algebra that follows.

#### Writing KCL at each node  

We adopt the sign convention “currents leaving a node are positive”.  

- **Node A**  
  \[
  G_1\,(V_1 - V_3) \;+\; G_2\,(V_1 - V_2) \;-\; I_0 \;=\; 0
  \]
  The first term is the current through \(R_1\) (leaving A toward C), the second term the current through \(R_2\) (leaving A toward B), and \(I_0\) is an external current source **entering** node A, hence the minus sign.

- **Node B** (similarly)  
  \[
  G_2\,(V_2 - V_1) \;+\; G_3\,(V_2 - V_{\text{L}}) \;+\; I_0 = 0
  \]
  (the exact form depends on the surrounding elements; the important point is that each branch contributes a term of the form \(G(V_{\text{node}}-V_{\text{adjacent}})\).)

- **Node C**  
  \[
  G_1\,(V_3 - V_1) \;+\; G_4\,(V_3 - V_{\text{L}}) \;+\; I_{\text{other}} = 0
  \]

These three equations capture the entire linear network.

### 2. Matrix Form of the Node Equations  

Collecting the coefficients of \(V_1, V_2, V_3\) we can write the system compactly as  

\[
\underbrace{\begin{bmatrix}
G_1+G_2 & -G_2      & -G_1 \\
-G_2    & G_2+G_3   & -G_3 \\
-G_1    & -G_3      & G_1+G_3
\end{bmatrix}}_{\displaystyle \mathbf{G}}
\begin{bmatrix}
V_1 \\ V_2 \\ V_3
\end{bmatrix}
=
\underbrace{\begin{bmatrix}
I_0 \\ 0 \\ 0
\end{bmatrix}}_{\displaystyle \mathbf{I}_s}
\]

Here \(\mathbf{G}\) is the **conductance matrix**, \(\mathbf{V}\) the column vector of node voltages, and \(\mathbf{I}_s\) the source‑current vector. The matrix is symmetric and positive‑definite for passive networks, guaranteeing a unique solution.

### 3. Solving for the Load‑Node Voltage  

Our ultimate goal is the voltage across the load, which in this configuration is simply \(V_2\) (the node that the load shares with the reference node). To isolate \(V_2\) we may apply **Cramer's rule**:

\[
V_2 = \frac{D_1}{D_2}
\]

- \(D_2\) is the determinant of the original conductance matrix \(\mathbf{G}\).  
- \(D_1\) is the determinant of the same matrix after **replacing the second column** (the column that multiplies \(V_2\)) with the source vector \(\mathbf{I}_s\).

Carrying out the determinant calculations (straightforward algebra for a \(3\times 3\) matrix) yields an expression for \(V_2\) that is a rational function of the conductances and the source current \(I_0\). Because all elements are linear, the relationship can be written in the canonical form

\[
V_2 = V_{\text{Th}} - I_{\text{load}}\,R_{\text{Th}}
\]

where \(I_{\text{load}} = V_2 / R_L\). Recognising the coefficients of \(I_{\text{load}}\) and the term independent of \(I_{\text{load}}\) gives us the **Thevenin voltage** \(V_{\text{Th}}\) and **Thevenin resistance** \(R_{\text{Th}}\).

### 4. Interpreting the Result – The Thevenin Equivalent  

The algebraic procedure above demonstrates that any linear network, no matter how many resistors, independent sources, or dependent sources it contains, can be collapsed to a single voltage source in series with a single resistance when observed from two terminals.  

- **Why it works:** The node‑voltage method reduces the network to a set of linear equations. Solving those equations for the terminal voltage produces a linear function of the terminal current. A linear function is precisely the I‑V characteristic of a series connection of an ideal voltage source and a resistor.  

- **What the parameters mean:**  
  * \(V_{\text{Th}}\) is the open‑circuit voltage at the terminals (the voltage when \(R_L \to \infty\)).  
  * \(R_{\text{Th}}\) is the input resistance seen looking back into the network with all independent sources

**Diagrams/board content from this segment:**

![~ NPTEL (captured at 5.0s)](extracted_images/video_test2_full/frame_5.0s.png)
*~ NPTEL (captured at 5.0s)*

![BASIC ELECTRONICS mst - (captured at 10.0s)](extracted_images/video_test2_full/frame_10.0s.png)
*BASIC ELECTRONICS mst - (captured at 10.0s)*

![The, Re Oe R ‘ oN How is V related tothe circuit parameters? (captured at 60.0s)](extracted_images/video_test2_full/frame_60.0s.png)
*The, Re Oe R ‘ oN How is V related tothe circuit parameters? (captured at 60.0s)*


---

## Deriving the Thevenin‑equivalent Expression for \(V_2\) with Cramer’s Rule  

In the previous discussion we introduced Cramer’s rule (also called Kramer's rule) to obtain the node voltage \(V_2\) as the ratio of two determinants.  Here we complete that derivation, expose the load‑dependence of the result, and recognize the familiar voltage‑division form that defines the Thevenin equivalent of the original network.

### 1.  The basic Cramer‑rule expression  

For the linear system \( \mathbf{G}\,\mathbf{v} = \mathbf{i} \) the voltage at node 2 is  

\[
V_2=\frac{\Delta_1}{\Delta}\; ,
\]

where  

* \(\Delta\)  – determinant of the original conductance matrix \(\mathbf{G}\);  
* \(\Delta_1\) – determinant of \(\mathbf{G}\) with its **second column** replaced by the right‑hand‑side current vector \(\mathbf{i}\).

A crucial observation is that **\(\Delta_1\) contains no appearance of the load conductance \(G_L\) (or, equivalently, the load resistance \(R_L\)).** Hence \(\Delta_1\) depends only on the internal circuit parameters (source resistance, internal conductances, etc.).

### 2.  Isolating the load term in the denominator  

The denominator \(\Delta\) **does** involve the load conductance \(G_L\).  By writing the column that contains \(G_L\) as the sum of two columns we can split \(\Delta\) into a part that is independent of \(G_L\) and a part that is linear in \(G_L\):

\[
\Delta \;=\; \underbrace{\Delta}_{\text{no }G_L}\;+\;G_L\,\underbrace{\Delta_2}_{\text{no }G_L}.
\]

* \(\Delta\) – the determinant of \(\mathbf{G}\) **with** the load term set to zero;  
* \(\Delta_2\) – the determinant of the matrix that remains after factoring the explicit \(G_L\) out of the column.  

Both \(\Delta\) and \(\Delta_2\) are independent of the load; only the scalar factor \(G_L\) carries the load dependence.

### 3.  Re‑expressing \(V_2\)  

Substituting the split denominator gives

\[
V_2=\frac{\Delta_1}{\Delta+G_L\Delta_2}.
\]

Because \(G_L = \dfrac{1}{R_L}\), we can rewrite the expression in a form that makes the load resistance explicit:

\[
V_2
   = \frac{\displaystyle \frac{\Delta_1}{\Delta}}
          {1+\displaystyle\frac{G_L\Delta_2}{\Delta}}
   = \frac{V_{2,\;{\rm OC}}}
          {1+\displaystyle\frac{\Delta_2}{\Delta}\,\frac{1}{R_L}} .
\]

Here  

\[
V_{2,\;{\rm OC}} \equiv \frac{\Delta_1}{\Delta}
\]

is the **open‑circuit voltage** (the value of \(V_2\) when the load is removed, i.e., \(R_L\!\to\!\infty\) so that \(G_L=0\)).

Multiplying numerator and denominator by \(R_L\) yields the classic voltage‑division formula:

\[
V_2 = \frac{R_L}{R_L+\displaystyle\frac{\Delta_2}{\Delta}}\;V_{2,\;{\rm OC}} .
\]

### 4.  Identification of the Thevenin resistance  

The ratio \(\displaystyle\frac{\Delta_2}{\Delta}\) carries the dimensions of resistance.  We therefore **define** the Thevenin resistance of the original network as  

\[
R_{\rm Th}\; \stackrel{\text{def}}{=}\; \frac{\Delta_2}{\Delta}.
\]

With this definition the expression for \(V_2\) becomes

\[
\boxed{\,V_2 = \frac{R_L}{R_L+R_{\rm Th}}\;V_{2,\;{\rm OC}}\,}.
\]

This is exactly the voltage‑division law for a **Thevenin equivalent circuit** consisting of:

* an ideal voltage source \(V_{\rm Th}=V_{2,\;{\rm OC}}\), and  
* a series resistance

**Diagrams/board content from this segment:**

![Thevenin Ri 5 Rev Ve can be found using Cramer's rule: Ve = (captured at 370.0s)](extracted_images/video_test2_full/frame_370.0s.png)
*Thevenin Ri 5 Rev Ve can be found using Cramer's rule: Ve = (captured at 370.0s)*

![az Ov nev Va can be found using Cramer's rule: Ve = Gs dex(6 (captured at 445.0s)](extracted_images/video_test2_full/frame_445.0s.png)
*az Ov nev Va can be found using Cramer's rule: Ve = Gs dex(6 (captured at 445.0s)*


---

## Thevenin’s Theorem – Replacing a Complex Network with a Simple Equivalent

When a linear circuit contains any combination of resistors, independent voltage and current sources, and linear dependent sources, **Thevenin’s theorem** guarantees that the whole network, as seen from two terminals (A‑B), can be replaced by a single voltage source \(V_{\mathrm{TH}}\) in series with a single resistance \(R_{\mathrm{TH}}\).  
The replacement is exact: any load resistor \(R_L\) connected between A and B experiences exactly the same voltage across it and the same current through it as it would in the original, more complicated network.

### Why the Replacement Works

Consider the original circuit and its Thevenin equivalent placed side‑by‑side, each driving the same load \(R_L\). Because both circuits are linear, the relationship between the load voltage \(V_L\) and the load current \(I_L\) is uniquely determined by the network’s internal behavior. If two circuits produce identical open‑circuit voltage (no load) and identical short‑circuit current (terminals forced together), then by the principle of superposition they must produce identical \(V_L\)–\(I_L\) characteristics for **any** value of \(R_L\). Hence the two circuits are interchangeable from the viewpoint of the load.

### Determining the Thevenin Voltage \(V_{\mathrm{TH}}\)

The Thevenin voltage is simply the **open‑circuit voltage** measured across the terminals A and B:

1. Disconnect any load (or simply leave the terminals open).  
2. Compute or measure the voltage that appears between A and B.  
3. That voltage, denoted \(V_{\!OC}\) (or \(V_{AB}\) with no load), equals \(V_{\mathrm{TH}}\).

Because no current flows in the open‑circuit condition, there is no voltage drop across \(R_{\mathrm{TH}}\); therefore the entire measured voltage appears across the Thevenin source itself.

### Determining the Thevenin Resistance \(R_{\mathrm{TH}}\)

Two complementary approaches are most common.

#### Method 1 – Deactivate All Independent Sources  

1. **Turn off** every independent voltage source (replace it with a short circuit) and every independent current source (replace it with an open circuit). Dependent sources remain active because their values depend on circuit variables.  
2. **Look into** the now‑inactive network from the terminals A‑B.  
3. The resistance you observe is \(R_{\mathrm{TH}}\).

Often the resulting resistance can be read directly by simplifying series‑parallel resistor groups. If inspection is difficult, a **test source** can be applied:

- Connect a known test voltage \(V_{\text{test}}\) across A‑B, measure the resulting test current \(I_{\text{test}}\), and compute  
  \[
  R_{\mathrm{TH}} = \frac{V_{\text{test}}}{I_{\text{test}}}.
  \]
- Alternatively, inject a test current and measure the resulting voltage; the ratio again yields \(R_{\mathrm{TH}}\).

#### Method 2 – Open‑Circuit Voltage and Short‑Circuit Current  

1. Find the open‑circuit voltage \(V_{\!OC}\) between A and B (this is \(V_{\mathrm{TH}}\) as above).  
2. Short the terminals A and B together and determine the resulting short‑circuit current \(I_{\!SC}\) that flows from A to B.  
3. Apply Ohm’s law to the Thevenin model: with the terminals shorted, the only voltage drop is across \(R_{\mathrm{TH}}\), so  
   \[
   R_{\mathrm{TH}} = \frac{V_{\!OC}}{I_{\!SC}}.
   \]

Both methods give the same resistance; the choice depends on which is more convenient for the particular circuit.

### Putting It All Together

Once \(V_{\mathrm{TH}}\) and \(R_{\mathrm{TH}}\) have been found, the original network can be replaced by the simple series combination shown below:

\[
\boxed{\text{Thevenin equivalent: } \; V_{\mathrm{TH}} \; \text{in series with} \; R_{\mathrm{TH}}}
\]

Any load resistor \(R_L\) connected across the terminals now experiences

\[
V_L = \frac{V_{\mathrm{TH}}}{1 + \dfrac{R_{\mathrm{TH}}}{R_L}}, \qquad
I_L = \frac{V_{\mathrm{TH}}}{R_{\mathrm{TH}} + R_L},
\]

exactly the same values that would be obtained from the original, more intricate circuit.

By mastering these two procedures—open‑circuit voltage measurement and source deactivation (or test‑source insertion)—students can systematically reduce even the most tangled linear networks to their elegant Thevenin equivalents, greatly simplifying analysis of power delivery, load behavior, and circuit design.

**Diagrams/board content from this segment:**

![Rr Circuit A A (resistors, ‘ sources, Vm Cevs, Coes, vevs, v (captured at 765.0s)](extracted_images/video_test2_full/frame_765.0s.png)
*Rr Circuit A A (resistors, ‘ sources, Vm Cevs, Coes, vevs, v (captured at 765.0s)*


---

## Finding Thevenin Parameters with Open‑Circuit Voltage and Short‑Circuit Current  

When a linear network is observed from a pair of terminals (A–B), its Thevenin equivalent consists of a single voltage source \(V_{\text{TH}}\) in series with a resistance \(R_{\text{TH}}\).  The open‑circuit voltage \(V_{\text{OC}}\) measured across the terminals equals the Thevenin voltage, because with no load there is no current flowing through \(R_{\text{TH}}\) and therefore no voltage drop on it:

\[
V_{\text{TH}} = V_{\text{OC}} .
\]

If the terminals are shorted, the current that flows, \(I_{\text{SC}}\), is the same as the short‑circuit current that would flow in the original network (denoted \(I_{\text{AC}}\) in the lecture).  Since the short forces the voltage across the terminals to zero, the whole Thevenin voltage appears across the internal resistance, giving

\[
I_{\text{SC}} = \frac{V_{\text{TH}}}{R_{\text{TH}}}
          = \frac{V_{\text{OC}}}{R_{\text{TH}}}.
\]

Re‑arranging yields a convenient expression for the Thevenin resistance:

\[
\boxed{ R_{\text{TH}} = \frac{V_{\text{OC}}}{I_{\text{SC}}} } .
\]

Notice that, unlike the “source‑deactivation” method, the open‑circuit/short‑circuit approach **does not require** turning off any independent sources; the original circuit is left untouched.

---

### Procedure Summary  

1. **Determine \(V_{\text{OC}}\):**  
   - Remove the load from terminals A–B.  
   - Compute the voltage that appears across the open terminals (this is \(V_{\text{TH}}\)).  

2. **Determine \(I_{\text{SC}}\):**  
   - Replace the load with a short circuit between A and B.  
   - Calculate the current that flows through the short (this is \(I_{\text{SC}}\)).  

3. **Calculate \(R_{\text{TH}}\):**  
   - Use \(R_{\text{TH}} = V_{\text{OC}} / I_{\text{SC}}\).

---

## Example 1 – A Simple Resistive Network  

Consider the circuit shown in the figure (a 9 V source feeding a 3 Ω resistor, a 9 Ω resistor, a 2 Ω resistor, and a 6 Ω resistor arranged as in the lecture).  

### Finding \(V_{\text{TH}}\)  

Removing the load reveals that no current flows through the 2 Ω resistor, so there is no voltage drop across it.  The open‑circuit voltage across A–B is therefore the voltage division between the 3 Ω and 9 Ω resistors:

\[
V_{\text{OC}} = V_{\text{TH}}

**Diagrams/board content from this segment:**

![Rn R OV, R (captured at 1175.0s)](extracted_images/video_test2_full/frame_1175.0s.png)
*Rn R OV, R (captured at 1175.0s)*

![rem: exampli so an Boy ts i R= Ovn Dy 3FR oy 8 Vn: 62 20 3A  (captured at 1225.0s)](extracted_images/video_test2_full/frame_1225.0s.png)
*rem: exampli so an Boy ts i R= Ovn Dy 3FR oy 8 Vn: 62 20 3A  (captured at 1225.0s)*

![4a. 20, on 20 20 (captured at 1290.0s)](extracted_images/video_test2_full/frame_1290.0s.png)
*4a. 20, on 20 20 (captured at 1290.0s)*

![Thev rem: a0 AB 40 20, ro 30 on Rov a2 AB 40 201 ne gre AB 4 (captured at 1335.0s)](extracted_images/video_test2_full/frame_1335.0s.png)
*Thev rem: a0 AB 40 20, ro 30 on Rov a2 AB 40 201 ne gre AB 4 (captured at 1335.0s)*


---

## Graphical Determination of Thevenin Parameters  

When a linear two‑terminal network is replaced by its Thevenin equivalent, the whole problem reduces to finding two numbers: the open‑circuit voltage \(V_{\text{TH}}\) (the voltage that appears across the terminals when no load is connected) and the Thevenin resistance \(R_{\text{TH}}\) (the resistance “seen” by any load placed across the same terminals.  In the example that has been developing throughout the lecture, the open‑circuit voltage is obtained by adding the two partial voltages that were already computed:

- The voltage across the 4‑Ω resistor, \(V_{AC}= I\cdot 4\;\Omega = 6\;\text{A}\times4\;\Omega = 24\;\text{V}\).  
- The voltage across the series combination of 12 Ω and 4 Ω, found by a voltage‑division of the 48 V source, is \(V_{CB}= \dfrac{12}{12+4}\times48\;\text{V}=36\;\text{V}\).

Hence the total voltage between terminals **A** and **B** is  

\[
V_{\text{OC}} = V_{AC}+V_{CB}=24\;\text{V}+36\;\text{V}=60\;\text{V}.
\]

Because the open‑circuit voltage is identical to the Thevenin voltage, we have  

\[
V_{\text{TH}} = 60\;\text{V}.
\]

The Thevenin resistance was previously determined by looking into the network with all independent sources turned off, which gave  

\[
R_{\text{TH}} = 7\;\Omega .
\]

---

### Using a Plot of Current versus Source Voltage  

A powerful visual method for extracting \(V_{\text{TH}}\) and \(R_{\text{TH}}\) is to attach an **external** voltage source across the two terminals and record the current that the source supplies as its voltage is varied.  

The governing relationship for the current \(I\) drawn from the source is the linear equation of the Thevenin model:

\[
I = \frac{V_{\text{TH}}-V}{R_{\text{TH}}}.
\]

Re‑arranging gives  

\[
V = V_{\text{TH}} - I R_{\text{TH}},
\]

which is the equation of a straight line with **negative slope** \(-\dfrac{1}{R_{\text{TH}}}\).  Plotting the measured current on the vertical axis against the source voltage on the horizontal axis therefore yields a line whose geometry directly reveals the Thevenin parameters:

| Feature of the line | How to obtain a Thevenin quantity |
|---------------------|-----------------------------------|
| **X‑intercept** (where \(I=0\)) | Set \(I=0\) in the equation → \(V = V_{\text{TH}}\).  The voltage at which the line crosses the horizontal axis is the open‑circuit voltage, i.e., \(V_{\text{TH}}\). |
| **Y‑intercept** (where \(V=0\)) | Set \(V=0\) → \(I = \dfrac{V_{\text{TH}}}{R_{\text{TH}}}\).  This current is the short‑circuit current \(I_{\text{SC}}\). |
| **Slope** | The slope equals \(-1/R_{\text{TH}}\).  Measuring the slope and taking its negative reciprocal yields the Thevenin resistance. |

In the simulation of the present circuit, the plotted line intersected the voltage axis at **60 V** and the current axis at **8.57 A**.  Consequently:

\[
I_{\text{SC}} = 8.57\;\text{A},\qquad
R_{\text{TH}} = \frac{V_{\text{TH}}}{I_{\text{SC}}}= \frac{60\;\text{V}}{8.57\;\text{A}}\approx 7\;\Omega .
\]

These values match exactly those obtained earlier by algebraic reduction, confirming the consistency of the graphical approach.

---

### Alternative Procedure: Varying a Load Resistor  

Instead of a variable voltage source, one may connect a **load resistor** \(R_L\) across the terminals, vary its resistance, and record the resulting terminal voltage \(V\) and load current \(I\).  Each choice of \(R_L\) yields a point \((V, I)\) that also lies on the same straight line described above, because the underlying Thevenin model remains unchanged.  By sweeping \(R_L\) over a suitable range, the same intercepts and slope can be extracted, providing the same \(V_{\text{TH}}\) and \(R_{\text{TH}}\).

---

### Summary  

- The open‑circuit voltage of the network is the sum of the two partial voltages, giving \(V_{\text{TH}} = 60\;\text{V}\).  
- The Thevenin resistance, previously calculated as the equivalent resistance seen with independent sources turned off, is \(R_{\text{TH}} = 7\;\Omega\).  
- Plotting the source current versus the source voltage yields a straight line whose X‑intercept is \(V_{\text{TH}}\), whose Y‑intercept is the short‑circuit current \(I_{\text{SC}} = V_{\text{TH}}/R_{\text{TH}} = 8.57\;\text{A}\), and whose slope \(-1/R_{\text{TH}}\) confirms the resistance value.  
- The same line can be generated by varying a load resistor rather than a voltage source, offering flexibility in experimental or simulation settings.  

Mastering this graphical technique equips you with a quick, visual means of characterising any linear two‑terminal network—a tool that proves invaluable when analysing RC circuits, amplifiers, and many other practical electronic systems.

**Diagrams/board content from this segment:**

![for finding Bo Vn, vn Ov ‘ Vn = v 1= ~T— (Note: negative slo (captured at 1505.0s)](extracted_images/video_test2_full/frame_1505.0s.png)
*for finding Bo Vn, vn Ov ‘ Vn = v 1= ~T— (Note: negative slo (captured at 1505.0s)*

![49 40 20 4 120 20 © 8 (captured at 1660.0s)](extracted_images/video_test2_full/frame_1660.0s.png)
*49 40 20 4 120 20 © 8 (captured at 1660.0s)*
