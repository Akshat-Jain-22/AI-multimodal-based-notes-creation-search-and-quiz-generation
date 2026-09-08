# Thevenin’s Theorem – Simplifying Linear Networks  

*This chapter develops the Thevenin equivalent for any linear, bilateral network.  Beginning with a node‑voltage analysis of a concrete circuit, we derive the open‑circuit voltage and Thevenin resistance using Cramer’s rule, present systematic procedures for obtaining these parameters, and finish with a graphical I‑V method that illustrates the same concepts.*  

---

## 1. From Node‑Voltage Analysis to the Thevenin Equivalent  

### 1.1 Setting up the example circuit  

Consider the network shown on the board, where a load resistor \(R_{L}\) is connected across two terminals.  We wish to determine the voltage \(V\) that appears across \(R_{L}\).  The node‑voltage method is used:

1. **Reference node** – the lower node of the diagram is taken as ground (\(0\;\text{V}\)).  
2. **Node potentials** – the remaining node voltages are labeled with respect to ground:  

   * Node A → \(V_{1}\)  
   * Node B → \(V_{2}\) (the node directly adjacent to the load)  
   * Node C → \(V_{3}\)

All elements are resistors, so we introduce conductances for algebraic convenience  

\[
G_{1}=\frac{1}{R_{1}},\qquad 
G_{2}=\frac{1}{R_{2}},\qquad 
G_{3}=\frac{1}{R_{3}},\;\dots
\]

### 1.2 Kirchhoff‑Current‑Law equations  

Applying KCL (currents leaving a node are taken as positive) gives  

\[
\begin{aligned}
\text{Node A:}&\quad G_{1}(V_{1}-V_{3}) + G_{2}(V_{1}-V_{2}) - I_{0}=0,\\[4pt]
\text{Node B:}&\quad \dots \\[4pt]
\text{Node C:}&\quad \dots
\end{aligned}
\]

Collecting the three equations in matrix form yields  

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

Here \(G\) is the **conductance matrix**, \(\mathbf{V}\) the vector of unknown node voltages, and \(\mathbf{I}_{s}\) the vector of independent source currents (only \(I_{0}\) appears).

### 1.3 Solving for the load voltage  

The quantity of interest is \(V_{2}\), because node B is the terminal of the load resistor \(R_{L}\) while the other terminal is ground.  Using Cramer’s rule,  

\[
V_{2}= \frac{D_{1}}{D_{2}},
\]

where  

* \(D_{2}= \det(G)\) (the determinant of the original matrix), and  
* \(D_{1}= \det\bigl(G\ \text{with its second column replaced by } I_{s}\bigr)\).

Carrying out the determinant calculations (the algebra is straightforward but lengthy) yields an expression for \(V_{2}\) that depends only on the conductances \(G_{i}\) and the source current \(I_{0}\).  Because \(V_{2}=V\), we have expressed the load voltage directly in terms of the underlying circuit parameters.

**Diagrams/board content from this segment:**

![~ NPTEL (captured at 5.0s)](extracted_images/video_test2_full/frame_5.0s.png)
*~ NPTEL (captured at 5.0s)*

![BASIC ELECTRONICS mst - (captured at 10.0s)](extracted_images/video_test2_full/frame_10.0s.png)
*BASIC ELECTRONICS mst - (captured at 10.0s)*

![The, Re Oe R ‘ oN How is V related tothe circuit parameters? (captured at 60.0s)](extracted_images/video_test2_full/frame_60.0s.png)
*The, Re Oe R ‘ oN How is V related tothe circuit parameters? (captured at 60.0s)*  

---

## 2. Cramer’s‑Rule Form of the Thevenin Equivalent  

### 2.1 Determinants that appear  

Define  

\[
\Delta_{1}= \det\!\bigl[G\ \text{with its second column replaced by the RHS vector}\bigr],
\qquad
\Delta = \det(G).
\]

A key observation is that \(\Delta_{1}\) contains **no** occurrence of the load conductance \(G_{L}=1/R_{L}\); it depends solely on the network elements that are *outside* the load.  

The determinant \(\Delta\) **does** involve \(G_{L}\) because the load column appears in the original matrix.  By writing that column as the sum of two simpler columns, the determinant can be split into a load‑free part and a part that is proportional to \(G_{L}\):

\[
\Delta = \Delta_{\text{free}} + G_{L}\,\Delta_{2},
\]

where \(\Delta_{2}\) is the determinant of the matrix obtained by replacing the load column with a column that contains **no** \(G_{L}\).  Both \(\Delta_{\text{free}}\) (which we simply denote \(\Delta\)) and \(\Delta_{2}\) are independent of the load.

### 2.2 Compact expression for the load voltage  

Substituting the determinant decomposition into the Cramer expression gives  

\[
V_{2}= \frac{\Delta_{1}}{\Delta+G_{L}\Delta_{2}}
      = \frac{\Delta_{1}}{\Delta\!\left(1+G_{L}\frac{\Delta_{2}}{\Delta}\right)} .
\]

Since only the factor \(G_{L}=1/R_{L}\) contains the load, the expression already has the classic Thevenin form.

### 2.3 Open‑circuit voltage  

When the load is removed (\(R_{L}\to\infty\Rightarrow G_{L}\to 0\)), the voltage reduces to  

\[
V_{2,\text{OC}} = \frac{\Delta_{1}}{\Delta}.
\]

Thus \(\displaystyle V_{\text{TH}} = V_{2,\text{OC}} = \frac{\Delta_{1}}{\Delta}\).

### 2.4 Thevenin resistance  

Define the **Thevenin resistance** as  

\[
R_{\text{TH}} \;\triangleq\; \frac{\Delta_{2}}{\Delta}.
\]

Because \(\Delta_{2}\) and \(\Delta\) are determinants of conductance matrices, their ratio has units of resistance (\(\Omega\)).  Using \(G_{L}=1/R_{L}\) the denominator of \(V_{2}\) becomes  

\[
\Delta\!\left(1+G_{L}R_{\text{TH}}\right)=\Delta\!\left(1+\frac{R_{\text{TH}}}{R_{L}}\right).
\]

Dividing numerator and denominator by \(\Delta\) and multiplying by \(R_{L}/R_{L}\) yields the familiar voltage‑division relationship  

\[
\boxed{\,V_{2}= \frac{R_{L}}{R_{L}+R_{\text{TH}}}\;V_{\text{TH}}\,}.
\]

**Interpretation** – The original network, as seen from the load terminals, behaves exactly like a Thevenin equivalent consisting of a source \(V_{\text{TH}}\) in series with a resistance \(R_{\text{TH}}\).  The parameters are **independent of the load**, which is why the model is so useful.

**Diagrams/board content from this segment:**

![Thevenin Ri 5 Rev Ve can be found using Cramer's rule: Ve = (captured at 370.0s)](extracted_images/video_test2_full/frame_370.0s.png)
*Thevenin Ri 5 Rev Ve can be found using Cramer's rule: Ve = (captured at 370.0s)*

![az Ov nev Va can be found using Cramer's rule: Ve = Gs dex(6 (captured at 445.0s)](extracted_images/video_test2_full/frame_445.0s.png)
*az Ov nev Va can be found using Cramer's rule: Ve = Gs dex(6 (captured at 445.0s)*  

---

## 3. General Statement of Thevenin’s Theorem  

For any linear two‑terminal network—no matter how many resistors, independent sources, or linear dependent sources it contains—**Thevenin’s theorem** guarantees that the network can be replaced, as seen from the terminals \(A\) and \(B\), by a single voltage source \(V_{\text{TH}}\) in series with a single resistance \(R_{\text{TH}}\).  The load resistor \(R_{L}\) experiences exactly the same voltage and current whether it is attached to the original network or to this simplified model.

### 3.1 Why the equivalent works  

* **Open‑circuit condition** (\(I_{L}=0\)): With no current flowing, there is no voltage drop across the series resistance, so the terminal voltage equals the source voltage.  Hence  

  \[
  V_{\text{TH}} = V_{\text{OC}} .
  \]

* **Load‑connected condition**: When a load \(R_{L}\) is attached, the circuit reduces to a classic series‑source problem  

  \[
  I_{L}= \frac{V_{\text{TH}}}{R_{\text{TH}}+R_{L}},\qquad
  V_{L}= I_{L}R_{L}= \frac{V_{\text{TH}}\,R_{L}}{R_{\text{TH}}+R_{L}} .
  \]

Because the Thevenin model reproduces both the open‑circuit voltage and the load behaviour, it is electrically indistinguishable from the original network at the terminals.

**Diagrams/board content from this segment:**

![Rr Circuit A A (resistors, ‘ sources, Vm Cevs, Coes, vevs, v (captured at 765.0s)](extracted_images/video_test2_full/frame_765.0s.png)
*Rr Circuit A A (resistors, ‘ sources, Vm Cevs, Coes, vevs, v (captured at 765.0s)*  

---

## 4. Practical Procedures for Finding \(V_{\text{TH}}\) and \(R_{\text{TH}}\)  

### 4.1 Determining the Thevenin voltage  

1. **Remove any load** connected between the terminals \(A\) and \(B\).  
2. **Measure or compute** the open‑circuit voltage \(V_{\text{OC}}\) across the terminals.  
3. Set  

   \[
   V_{\text{TH}} = V_{\text{OC}} .
   \]

### 4.2 Determining the Thevenin resistance  

Two complementary methods are commonly employed.

#### Method 1 – Deactivating independent sources  

* Replace every independent voltage source by a short circuit.  
* Replace every independent current source by an open circuit.  

The resistance seen looking into the terminals is then \(R_{\text{TH}}\).  
If the resulting network is not trivially reducible, a **test source** can be introduced:

* **Test‑voltage source** \(V_{\text{test}}\) across the terminals produces a current \(I_{\text{test}}\); then  

  \[
  R_{\text{TH}} = \frac{V_{\text{test}}}{I_{\text{test}}}.
  \]

* **Test‑current source** \(I_{\text{test}}\) produces a voltage \(V_{\text{test}}\); then  

  \[
  R_{\text{TH}} = \frac{V_{\text{test}}}{I_{\text{test}}}.
  \]

Because the network is linear, both approaches give the same result.

#### Method 2 – Using open‑circuit and short‑circuit values  

1. Compute (or measure) the open‑circuit voltage \(V_{\text{OC}} = V_{\text{TH}}\).  
2. **Short the terminals** (\(V=0\)) and determine the resulting short‑circuit current \(I_{\text{SC}}\).  
3. Apply Ohm’s law to the Thevenin model:  

   \[
   R_{\text{TH}} = \frac{V_{\text{TH}}}{I_{\text{SC}}}
                = \frac{V_{\text{OC}}}{I_{\text{SC}}}.
   \]

### 4.3 Summary of the step‑by‑step procedure  

| Step | Action | Result |
|------|--------|--------|
| 1 | Remove any load between \(A\) and \(B\). | Isolate the network. |
| 2 | Find the open‑circuit voltage \(V_{\text{OC}}\). | \(V_{\text{TH}} = V_{\text{OC}}\). |
| 3 | Either (a) deactivate independent sources and measure the “look‑in” resistance, **or** (b) short the terminals and measure \(I_{\text{SC}}\). | Obtain \(R_{\text{TH}}\). |
| 4 | Assemble the Thevenin equivalent: a source \(V_{\text{TH}}\) in series with \(R_{\text{TH}}\). | The load sees an identical electrical environment. |

---

## 5. Graphical (I‑V) Method for Determining the Thevenin Parameters  

### 5.1 Constructing the I‑V plot  

1. Replace the original network by its Thevenin equivalent \((V_{\text{TH}},R_{\text{TH}})\).  
2. Connect an external variable voltage source \(V\) across the terminals \(A\)–\(B\).  
3. For each chosen value of \(V\), compute (or measure) the current \(I\) that flows into the Thevenin circuit.  

Because only the series resistor \(R_{\text{TH}}\) lies between the external source and ground, the current obeys  

\[
I = \frac{V_{\text{TH}}-V}{R_{\text{TH}}}.
\]

This is the equation of a straight line with slope \(-1/R_{\text{TH}}\).

### 5.2 Interpreting the straight line  

* **V‑axis intercept** (\(I=0\)) occurs at \(V = V_{\text{TH}}\); it directly reads the Thevenin voltage.  
* **I‑axis intercept** (\(V=0\)) gives the short‑circuit current  

  \[
  I_{\text{SC}} = \frac{V_{\text{TH}}}{R_{\text{TH}}}.
  \]

From the plotted line we obtain both \(V_{\text{TH}}\) and \(I_{\text{SC}}\), and consequently  

\[
R_{\text{TH}} = \frac{V_{\text{TH}}}{I_{\text{SC}}}.
\]

### 5.3 Numerical example  

A simulation (SEQUEL file *ee101.thevenin_1.sqpr*) swept the external voltage and produced the following straight line:

* **V‑intercept:** \(60\;\text{V}\) → \(V_{\text{TH}} = 60\;\text{V}\).  
* **I‑intercept:** \(8.57\;\text{A}\) →  

  \[
  R_{\text{TH}} = \frac{60\;\text{V}}{8.57\;\text{A}} \approx 7\;\Omega .
  \]

Thus the Thevenin equivalent of the original circuit is a **60‑V source in series with a 7‑Ω resistor**, exactly the same result obtained earlier by algebraic reduction.

### 5.4 Alternate graphical approach – varying a load resistor  

Instead of imposing a separate voltage source, one may connect a **variable load resistor** \(R_{L}\) across the terminals and record the terminal voltage \(V\) together with the load current \(I = V/R_{L}\).  Sweeping \(R_{L}\) from a large (open‑circuit) value down to near zero (short circuit) yields the same straight‑line I‑V plot, confirming that the Thevenin parameters are intrinsic to the network and independent of the test method.

**Diagrams/board content from this segment:**

![for finding Bo Vn, vn Ov ‘ Vn = v 1= ~T— (Note: negative slo (captured at 1505.0s)](extracted_images/video_test2_full/frame_1505.0s.png)
*for finding Bo Vn, vn Ov ‘ Vn = v 1= ~T— (Note: negative slo (captured at 1505.0s)*

![49 40 20 4 120 20 © 8 (captured at 1660.0s)](extracted_images/video_test2_full/frame_1660.0s.png)
*49 40 20 4 120 20 © 8 (captured at 1660.0s)*  

---

## 6. Closing Summary – Key Takeaways  

- **Thevenin’s theorem** reduces any linear two‑terminal network to a single voltage source \(V_{\text{TH}}\) in series with a resistance \(R_{\text{TH}}\).  
- \(V_{\text{TH}}\) equals the **open‑circuit voltage** \(V_{\text{OC}}\) measured at the terminals with the load removed.  
- \(R_{\text{TH}}\) can be found either by **deactivating independent sources** and measuring the “look‑in” resistance, or by the ratio \(R_{\text{TH}} = V_{\text{OC}}/I_{\text{SC}}\) using the **short‑circuit current**.  
- Using **Cramer’s rule**, the load voltage can be expressed as \(V = \dfrac{R_{L}}{R_{L}+R_{\text{TH}}}\,V_{\text{TH}}\), making the voltage‑division nature of the theorem explicit.  
- A **graphical I‑V method** provides a visual way to read both \(V_{\text{TH}}\) (V‑intercept) and \(I_{\text{SC}}\) (I‑intercept), from which \(R_{\text{TH}}\) follows immediately.  

These tools together give engineers a powerful, systematic way to analyze and design circuits without repeatedly solving large networks for each new load condition.