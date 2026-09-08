# thevenin

## Thevenin’s Theorem – From Node‑Voltage Analysis to an Equivalent Circuit  

A powerful way to simplify any linear, bilateral network is to replace it with a **Thevenin equivalent**: a single voltage source \(V_{\mathrm{th}}\) in series with a resistance \(R_{\mathrm{th}}\).  The theorem tells us that, as far as a particular pair of terminals is concerned, the entire network behaves exactly like that simple two‑element circuit.  Before we can state the theorem formally, it is useful to see how the equivalent parameters emerge from a systematic analysis of a concrete circuit.

### 1. Setting up the example  

Consider the network shown on the board, in which a load resistor \(R_{L}\) is connected across two terminals.  We are interested in the voltage \(V\) that appears across \(R_{L}\).  To obtain a relationship between \(V\) and the surrounding components we adopt the **node‑voltage method**:

1. **Choose a reference node** (ground).  The instructor selected the lower node of the diagram, assigning it a potential of \(0\ \text{V}\).  
2. **Label the remaining node potentials** with respect to ground:  
   - Node A → \(V_{1}\)  
   - Node B → \(V_{2}\) (the node directly adjacent to the load)  
   - Node C → \(V_{3}\)

All circuit elements are resistors, so we introduce **conductances** for convenience:
\[
G_{1}=\frac{1}{R_{1}},\qquad G_{2}=\frac{1}{R_{2}},\qquad \ldots
\]
Using conductance simplifies the algebra because each current becomes a product of a conductance and a voltage difference.

### 2. Writing KCL equations  

Kirchhoff’s Current Law (KCL) states that the algebraic sum of currents leaving any node is zero.  Taking currents that leave a node as positive, the KCL equations become:

- **Node A**  
  \[
  G_{1}(V_{1}-V_{3})\;+\;G_{2}(V_{1}-V_{2})\;-\;I_{0}=0
  \]
  The first term is the current through \(R_{1}\) (leaving A toward C), the second term the current through \(R_{2}\) (leaving A toward B), and \(-I_{0}\) accounts for the external current source \(I_{0}\) that *enters* node A.

- **Node B** and **Node C** are written analogously, each expressing the sum of the conductance‑weighted voltage differences plus any independent current sources.

These three equations can be assembled compactly in matrix form:
\[
\underbrace{\begin{bmatrix}
G_{1}+G_{2} & -G_{2} & -G_{1}\\[4pt]
-\,G_{2} & G_{2}+G_{3} & -G_{3}\\[4pt]
-\,G_{1} & -G_{3} & G_{1}+G_{3}
\end{bmatrix}}_{\displaystyle G}
\begin{bmatrix}
V_{1}\\ V_{2}\\ V_{3}
\end{bmatrix}
=
\underbrace{\begin{bmatrix}
I_{0}\\ 0\\ 0
\end{bmatrix}}_{\displaystyle I_{s}}
\tag{1}
\]
Here **\(G\)** is the *conductance matrix* (a \(3\times3\) symmetric matrix), **\(V\)** is the column vector of unknown node voltages, and **\(I_{s}\)** contains the independent source currents (only \(I_{0}\) appears because the other nodes have no external injections).

### 3. Solving for the load voltage  

Our goal is the voltage across the load, which is precisely \(V_{2}\) because node B is the terminal of \(R_{L}\) while the other terminal is ground (node B’s voltage relative to ground).  Equation (1) is a linear system, and a convenient analytic tool for a single unknown is **Cramer’s rule**:

\[
V_{2}= \frac{D_{1}}{D_{2}}
\]

- **\(D_{2}\)** is the determinant of the original conductance matrix \(G\).  
- **\(D_{1}\)** is the determinant of the matrix obtained by replacing the *second* column of \(G\) (the column that multiplies \(V_{2}\)) with the source vector \(I_{s}\).

Carrying out the determinant calculations (the algebra is straightforward but lengthy) yields an expression for \(V_{2}\) that depends only on the conductances \(G_{i}\) and the source current \(I_{0}\).  Because \(V_{2}=V\), we have now expressed the load voltage directly in terms of the underlying circuit parameters.

### 4. Interpreting the result – the Thevenin equivalent  

The expression for \(V\) can be rearranged into the familiar Thevenin form
\[
V = V_{\mathrm{th}}\; \frac{R_{L

**Diagrams/board content from this segment:**

![~ NPTEL (captured at 5.0s)](extracted_images/video_test2_full/frame_5.0s.png)
*~ NPTEL (captured at 5.0s)*

![BASIC ELECTRONICS mst - (captured at 10.0s)](extracted_images/video_test2_full/frame_10.0s.png)
*BASIC ELECTRONICS mst - (captured at 10.0s)*

![The, Re Oe R ‘ oN How is V related tothe circuit parameters? (captured at 60.0s)](extracted_images/video_test2_full/frame_60.0s.png)
*The, Re Oe R ‘ oN How is V related tothe circuit parameters? (captured at 60.0s)*


---

## Thevenin‑Equivalent Form of \(V_2\) Using Cramer’s Rule  

When the node voltage \(V_2\) is expressed with Cramer’s rule, the result is a ratio of two determinants.  
Let  

\[
\Delta_1=\det\bigl[G\;\text{with its second column replaced by the RHS vector}\bigr]
\]

and  

\[
\Delta=\det(G)
\]

where \(G\) is the original conductance matrix of the network.  

### Key observations about the determinants  

* **Independence of the load.**  
  \(\Delta_1\) contains **no** occurrence of the load conductance \(G_L\;(=1/R_L)\); consequently its value is fixed by the circuit elements that are *outside* the load.  

* **Dependence of \(\Delta\) on the load.**  
  The determinant \(\Delta\) does involve the entry \(G_L\) in the column that corresponds to the load branch. By writing that column as the sum of two simpler columns  

  \[
  \underbrace{\begin{bmatrix}1\\0\\0\end{bmatrix}}_{\text{column 1}}-
  \underbrace{\begin{bmatrix}G_2\\0\\G_2\end{bmatrix}}_{\text{column 2}}+
  \underbrace{\begin{bmatrix}0\\G_L\\0\end{bmatrix}}_{\text{column 3}},
  \]

  the determinant can be split into the sum of two determinants: one that **does not** contain \(G_L\) and one that **does**.  

  Denote the load‑free part by \(\Delta\) and factor the conductance term out of the second part:

  \[
  \Delta = \Delta\;+\;G_L\,\Delta_2 ,
  \]

  where  

  \[
  \Delta_2 = \det\!\Bigl[\;G\ \text{with the load column replaced by a column that has no }G_L\Bigr].
  \]

  By construction \(\Delta_2\) is also independent of the load.

### Compact expression for \(V_2\)

Putting the pieces together,

\[
V_2 = \frac{\Delta_1}{\Delta+G_L\Delta_2}
      = \frac{\Delta_1}{\Delta\bigl(1+G_L\frac{\Delta_2}{\Delta}\bigr)} .
\]

Because \(\Delta_1,\Delta,\Delta_2\) are all load‑free, the **only** place where the load appears is the factor \(G_L\).  

### Open‑circuit voltage \(V_{2,\text{OC}}\)

The open‑circuit condition corresponds to an infinite load resistance \((R_L\to\infty)\), so \(G_L=1/R_L\to 0\).  
Setting \(G_L=0\) in the expression above gives

\[
V_{2,\text{OC}} = \frac{\Delta_1}{\Delta}.
\]

Thus \(\displaystyle \frac{\Delta_1}{\Delta}\) is precisely the open‑circuit voltage at node 2.

### Introducing the Thevenin resistance  

Define the **Thevenin resistance** seen by the load as  

\[
R_{\text{TH}} \; \triangleq\; \frac{\Delta_2}{\Delta}.
\]

Note that \(R_{\text{TH}}\) has the dimensions of resistance because \(\Delta_2\) and \(\Delta\) are both determinants of conductance matrices (the ratio therefore carries units of \(\text{S}^{-1}=\Omega\)).  

Since \(G_L = 1/R_L\), the denominator of the \(V_2\) expression becomes

\[
\Delta\bigl(1+G_LR_{\text{TH}}\bigr)=\Delta\Bigl(1+\frac{R_{\text{TH}}}{R_L}\Bigr).
\]

Dividing numerator and denominator by \(\Delta\) and then multiplying the whole fraction by \(R_L/R_L\) yields the familiar voltage‑division form

\[
\boxed{\,V_2 = \frac{R_L}{R_L+R_{\text{TH}}}\;V_{2,\text{OC}}\,}.
\]

### Interpretation  

The derived formula tells us that the original network, as seen from the load terminals, behaves exactly like a **Thevenin equivalent circuit**:

* a single ideal voltage source of magnitude \(V_{2,\text{OC}}\) (the open‑circuit voltage), and  
* a series resistance \(R_{\text{TH}} = \Delta_2/\Delta\) (the Thevenin resistance).

When the load \(R_L\) is connected, the voltage appearing across it is simply the result of a voltage divider formed by \(R_{\text{TH}}\) and \(R_L\).  

Because \(\Delta_1, \Delta,\) and \(\Delta_2\) depend only on the internal components (source resistances, internal conductances, etc.), the Thevenin parameters are **independent of the load**. This independence is what makes the Thevenin model a powerful tool for analyzing how any load will respond without recomputing the entire circuit each time.

**Diagrams/board content from this segment:**

![Thevenin Ri 5 Rev Ve can be found using Cramer's rule: Ve = (captured at 370.0s)](extracted_images/video_test2_full/frame_370.0s.png)
*Thevenin Ri 5 Rev Ve can be found using Cramer's rule: Ve = (captured at 370.0s)*

![az Ov nev Va can be found using Cramer's rule: Ve = Gs dex(6 (captured at 445.0s)](extracted_images/video_test2_full/frame_445.0s.png)
*az Ov nev Va can be found using Cramer's rule: Ve = Gs dex(6 (captured at 445.0s)*


---

## Thevenin’s Theorem – Re‑representing a Complex Network by a Simple Source‑Resistance Pair  

When a circuit contains any combination of resistors, independent voltage or current sources, and linear dependent sources, Thevenin’s theorem guarantees that **the entire network, as seen from two terminals A and B, can be replaced by a single voltage source \(V_{\text{TH}}\) in series with a single resistance \(R_{\text{TH}}\)**.  
The load resistor \(R_L\) connected across A–B experiences exactly the same voltage and current whether it is attached to the original network or to this simplified Thevenin equivalent.

### Why the Equivalent Works  

* **Open‑circuit condition:** If the terminals A–B are left open (no load), the current flowing is zero, so there is no voltage drop across the series resistance. Consequently the voltage measured at the terminals of the original network—denoted \(V_{\text{OC}}\)—must equal the voltage of the Thevenin source:
  \[
  V_{\text{TH}} = V_{\text{OC}} .
  \]
  This relationship follows directly from the definition of an open circuit: the only element that can sustain a voltage is the source itself.

* **Load‑connected condition:** When a load \(R_L\) is attached, the circuit reduces to a classic series‑source problem:
  \[
  I_L = \frac{V_{\text{TH}}}{R_{\text{TH}}+R_L},
  \qquad
  V_L = I_L\,R_L = \frac{V_{\text{TH}}\,R_L}{R_{\text{TH}}+R_L}.
  \]
  Because the original network and its Thevenin model are electrically indistinguishable at A–B, these expressions give the exact load current and voltage that the original circuit would produce.

### Determining the Thevenin Voltage \(V_{\text{TH}}\)

1. **Remove any load** that might be connected between A and B.  
2. **Measure (or calculate) the open‑circuit voltage** across the terminals; this is \(V_{\text{OC}}\).  
3. Set  
   \[
   V_{\text{TH}} = V_{\text{OC}} .
   \]

Thus, the Thevenin voltage is simply the voltage that the original network would present to an infinite‑impedance load.

### Determining the Thevenin Resistance \(R_{\text{TH}}\)

Two complementary procedures are commonly used.

#### Method 1 – Deactivate All Independent Sources  

* **Independent voltage sources** are replaced by short circuits (their internal resistance is assumed zero).  
* **Independent current sources** are replaced by open circuits (their internal resistance is assumed infinite).  

After this de‑activation, the resistance seen looking into the terminals A–B is exactly \(R_{\text{TH}}\).  
In many practical networks this “look‑in” resistance can be read directly by inspection; when the remaining elements are not trivially reducible, a **test source** may be introduced:

* **Test‑voltage source** \(V_{\text{test}}\) placed across A–B produces a current \(I_{\text{test}}\); then  
  \[
  R_{\text{TH}} = \frac{V_{\text{test}}}{I_{\text{test}}}.
  \]
* **Test‑current source** \(I_{\text{test}}\) placed across A–B produces a voltage \(V_{\text{test}}\); then  
  \[
  R_{\text{TH}} = \frac{V_{\text{test}}}{I_{\text{test}}}.
  \]

Either approach yields the same resistance, because the network is linear.

#### Method 2 – Use Open‑Circuit and Short‑Circuit Values  

1. **Find the open‑circuit voltage** \(V_{\text{OC}}\) (already identified as \(V_{\text{TH}}\)).  
2. **Short the terminals A–B** and determine the resulting short‑circuit current \(I_{\text{SC}}\) that flows from A to B.  
3. Apply Ohm’s law to the Thevenin model:
   \[
   R_{\text{TH}} = \frac{V_{\text{TH}}}{I_{\text{SC}}}
                = \frac{V_{\text{OC}}}{I_{\text{SC}}}.
   \]

Because the Thevenin equivalent must reproduce both the open‑circuit voltage and the short‑circuit current of the original network, this ratio uniquely defines \(R_{\text{TH}}\).

### Summary of the Procedure  

| Step | Action | Result |
|------|--------|--------|
| 1 | Remove any load between A and B. | Isolate the network. |
| 2 | Compute (or measure) the open‑circuit voltage \(V_{\text{OC}}\). | \(V_{\text{TH}} = V_{\text{OC}}\). |
| 3 | Deactivate all independent sources **or** short A–B and find \(I_{\text{SC}}\). | Obtain \(R_{\text{TH}}\) either by direct resistance inspection, \(R_{\text{TH}} = V_{\text{test}}/I_{\text{test}}\), or by \(R_{\text{TH}} = V_{\text{TH}}/I_{\text{SC}}\). |
| 4 | Assemble the Thevenin equivalent: a source \(V_{\text{TH}}\) in series with \(R_{\text{TH}}\). | The load \(R_L\) sees an identical electrical environment. |

With these steps, any linear two‑terminal network—no matter how intricate—can be collapsed to a **single voltage source and a single series resistance**, greatly simplifying analysis, design, and troubleshooting.

**Diagrams/board content from this segment:**

![Rr Circuit A A (resistors, ‘ sources, Vm Cevs, Coes, vevs, v (captured at 765.0s)](extracted_images/video_test2_full/frame_765.0s.png)
*Rr Circuit A A (resistors, ‘ sources, Vm Cevs, Coes, vevs, v (captured at 765.0s)*


---

## Determining the Thevenin Equivalent with the Open‑Circuit Voltage and Short‑Circuit Current

When a linear network is viewed from a pair of terminals (say, A–B), its external behaviour can always be represented by a **Thevenin equivalent**: a single voltage source \(V_{\text{TH}}\) in series with a resistance \(R_{\text{TH}}\).  
Two quantities that are directly measurable from the original circuit are especially useful:

* **Open‑circuit voltage** \(V_{\!OC}\) – the voltage that appears across the terminals when no load is connected (i.e., the load current is zero).  
* **Short‑circuit current** \(I_{\!SC}\) – the current that would flow if the terminals were connected together with an ideal wire (i.e., the terminal voltage is forced to zero).

Because the Thevenin resistance is the ratio of these two quantities, the relationship

\[
I_{\!SC}= \frac{V_{\!OC

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

## Determining the Thevenin Equivalent by a Graphical (I‑V) Method  

In the preceding analysis we found the open‑circuit voltage between terminals **A** and **B** by adding the two partial voltages obtained from the original network:  

\[
V_{AB}=V_{AC}+V_{CB}=24\;{\rm V}+36\;{\rm V}=60\;{\rm V}.
\]

Because the open‑circuit voltage is identical to the Thevenin voltage, we have  

\[
V_{\text{TH}} = V_{OC}=60\ \text{V}.
\]

The remaining task is to obtain the Thevenin resistance \(R_{\text{TH}}\). One convenient way is to use a **graphical method** that plots the current flowing between the terminals as a function of an externally applied voltage.  

### 1. Constructing the I‑V plot  

1. **Replace the original network by its Thevenin equivalent** – a voltage source \(V_{\text{TH}}\) in series with a resistor \(R_{\text{TH}}\).  
2. **Connect an external variable voltage source** \(V\) across the Thevenin terminals (the same points A‑B).  
3. **Measure (or compute) the resulting current** \(I\) that flows from the source into the Thevenin circuit for each value of \(V\).  

Because the only series element besides the external source is \(R_{\text{TH}}\), the current obeys  

\[
I = \frac{V_{\text{TH}}-V}{R_{\text{TH}}}.
\]

This equation is a straight line with a **negative slope** of \(-\dfrac{1}{R_{\text{TH}}}\).  

### 2. Interpreting the line  

- **V‑axis intercept** (where \(I=0\)): setting \(I=0\) gives \(V = V_{\text{TH}}\). Thus the point where the line crosses the voltage axis directly reads the Thevenin voltage, which we already know to be \(60\ \text{V}\).  
- **I‑axis intercept** (where \(V=0\)): setting \(V=0\) yields  

  \[
  I_{\text{SC}} = \frac{V_{\text{TH}}}{R_{\text{TH}}},
  \]

  the **short‑circuit current** that would flow if the terminals were tied together with an ideal wire.  

From the plotted line we can therefore read both \(V_{\text{TH}}\) (the V‑intercept) and \(I_{\text{SC}}\) (the I‑intercept).  

### 3. Extracting the numerical values  

Running the simulation (the SEQUEL file *ee101.thevenin_1.sqpr*) and sweeping the external voltage produced the following straight‑line graph:

- **V‑intercept:** \(V = 60\ \text{V}\) – confirming \(V_{\text{TH}} = 60\ \text{V}\).  
- **I‑intercept:** \(I = 8.57\ \text{A}\).  

Using the relationship \(R_{\text{TH}} = V_{\text{TH}}/I_{\text{SC}}\),

\[
R_{\text{TH}} = \frac{60\ \text{V}}{8.57\ \text{A}} \approx 7\ \Omega.
\]

Thus the Thevenin equivalent of the original circuit is a **60‑V source in series with a 7‑Ω resistor**, exactly the same result obtained earlier by algebraic reduction.

### 4. Alternate graphical approach – varying a load resistor  

Instead of imposing an external voltage source, one may connect a **variable load resistor \(R_L\)** across the terminals and record the terminal voltage \(V\) together with the load current \(I = V/R_L\). As \(R_L\) is swept from a very high value (open circuit) down to near zero (short circuit), the same straight line appears on an I‑V plot, yielding identical intercepts. This method emphasizes that the Thevenin parameters are intrinsic to the network and do not depend on the particular way the test source is applied.

### 5. Why the method works  

The linear relationship stems directly from Ohm’s law applied to the series combination of \(V_{\text{TH}}\) and \(R_{\text{TH}}\). Any linear two‑terminal network can be reduced to this form; therefore, a single straight‑line plot contains all the information needed to reconstruct the Thevenin model. The negative slope reflects the fact that increasing the externally applied voltage reduces the net voltage across the internal resistor, thereby decreasing the current.

### 6. Summary of the graphical technique  

- Replace the original circuit by its Thevenin model \((V_{\text{TH}}, R_{\text{TH}})\).  
- Apply a variable voltage (or vary a load resistor) and record the resulting current.  
- Plot \(I\) versus \(V\); the line will have slope \(-1/R_{\text{TH}}\).  
- The V‑axis intercept gives \(V_{\text{TH}}\); the I‑axis intercept gives \(I_{\text{SC}}\).  
- Compute \(R_{\text{TH}} = V_{\text{TH}}/I_{\text{SC}}\).  

Using this procedure on the example circuit yields \(V_{\text{TH}} = 60\ \text{V}\) and \(R_{\text{TH}} = 7\ \Omega\), confirming the earlier analytical results and reinforcing the utility of Thevenin’s theorem for simplifying complex networks.

**Diagrams/board content from this segment:**

![for finding Bo Vn, vn Ov ‘ Vn = v 1= ~T— (Note: negative slo (captured at 1505.0s)](extracted_images/video_test2_full/frame_1505.0s.png)
*for finding Bo Vn, vn Ov ‘ Vn = v 1= ~T— (Note: negative slo (captured at 1505.0s)*

![49 40 20 4 120 20 © 8 (captured at 1660.0s)](extracted_images/video_test2_full/frame_1660.0s.png)
*49 40 20 4 120 20 © 8 (captured at 1660.0s)*
