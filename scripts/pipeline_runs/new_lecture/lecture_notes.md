# new lecture

## Thevenin’s Theorem – From a Complex Network to an Equivalent Voltage Source  

Theorem 1 (Thevenin). *Any linear bilateral network, when observed from a pair of terminals, can be replaced by a single ideal voltage source \(V_{\text{th}}\) in series with a resistance \(R_{\text{th}}\).*  
The two parameters \(V_{\text{th}}\) (Thevenin voltage) and \(R_{\text{th}}\) (Thevenin resistance) are completely determined by the elements that lie inside the network; the external load sees exactly the same voltage‑current relationship whether the original circuit or its Thevenin equivalent is connected.

### Why an Equivalent Exists  

A linear circuit obeys the superposition principle: the response at any terminal is a linear combination of the independent sources. Consequently the terminal voltage \(V\) is an affine (i.e., linear plus constant) function of the load current \(I_{\!L}\):

\[
V = V_{\text{oc}} - I_{\!L}\,R_{\text{eq}} .
\]

Here \(V_{\text{oc}}\) is the open‑circuit voltage (the voltage that appears when the load is removed, \(I_{\!L}=0\)). The slope \(-R_{\text{eq}}\) is the same for every load because the internal resistance of a linear network is independent of the external connection. Re‑arranging the expression gives the familiar series‑source form

\[
V = V_{\text{th}} - I_{\!L} R_{\text{th}},
\qquad\text{with } V_{\text{th}}=V_{\text{oc}},\; R_{\text{th}}=R_{\text{eq}} .
\]

Thus any linear network can be collapsed to a Thevenin source that reproduces exactly the same \(V\)–\(I_{\!L}\) line.

### Extracting the Thevenin Parameters – An Illustrative Example  

Consider the circuit shown in the figure (load resistor \(R_{L}\) connected across terminals \(A\)–\(B\)). The goal is to determine the voltage \(V\) across \(R_{L}\) as a function of the surrounding resistors and the independent current source \(I_{0}\).

#### 1. Assign Node Voltages  

Choose a reference node (ground) at the bottom of the diagram. The remaining node voltages are defined as  

\[
\begin{aligned}
V_{1}&=\text{voltage at node }A,\\
V_{2}&=\text{voltage at node }B\;(=0\text{ V for the reference}),\\
V_{3}&=\text{voltage at node }C .
\end{aligned}
\]

#### 2. Replace Resistances by Conductances  

For algebraic convenience, introduce conductances  

\[
G_{1}= \frac{1}{R_{1}},\qquad
G_{2}= \frac{1}{R_{2}},\qquad
G_{3}= \frac{1}{R_{3}},\;\dots
\]

so that a current through a resistor can be written as \(G\,(V_{\text{high}}-V_{\text{low}})\).

#### 3. Write KCL at Each Node  

Take currents **leaving** a node as positive.  

*Node A*  

\[
G_{1}(V_{1}-V_{3})\;+\;G_{2}(V_{1}-V_{2})\;-\;I_{0}=0 .
\tag{1}
\]

The first term is the current through \(R_{1}\) toward node C, the second term the current through \(R_{2}\) toward node B, and \(I_{0}\) enters node A (hence the minus sign).

*Node B*  

\[
G_{2}(V_{2}-V_{1})\;+\;G_{3}(V_{2}-V_{3})=0 .
\tag{2}
\]

*Node C*  

\[
G_{1}(V_{3}-V_{1})\;+\;G_{3}(V_{3}-V_{2})\;+I_{0}=0 .
\tag{3}
\]

#### 4. Assemble the Matrix Equation  

Equations (1)–(3) can be written compactly as  

\[
\underbrace{\begin{bmatrix}
 G_{1}+G_{2} & -G_{2} & -G_{1}\\[2pt]
 -G_{2} & G_{2}+G_{3} & -G_{3}\\[2pt]
 -G_{1} & -G_{3} & G_{1}+G_{3}
\end{bmatrix}}_{\displaystyle \mathbf{G}}
\;
\underbrace{\begin{bmatrix}
V_{1}\\ V_{2}\\ V_{3}
\end{bmatrix}}_{\displaystyle \mathbf{V}}
=
\underbrace{\begin{bmatrix}
 I_{0}\\ 0\\ -I_{0}
\end{bmatrix}}_{\displaystyle \mathbf{I}_{s}} .
\tag{4}
\]

\(\mathbf{G

**Diagrams/board content from this segment:**

![~ NPTEL (captured at 5.0s)](extracted_images/video_test2_full/frame_5.0s.png)
*~ NPTEL (captured at 5.0s)*

![BASIC ELECTRONICS mst - (captured at 10.0s)](extracted_images/video_test2_full/frame_10.0s.png)
*BASIC ELECTRONICS mst - (captured at 10.0s)*

![The, Re Oe R ‘ oN How is V related tothe circuit parameters? (captured at 60.0s)](extracted_images/video_test2_full/frame_60.0s.png)
*The, Re Oe R ‘ oN How is V related tothe circuit parameters? (captured at 60.0s)*


---

## Deriving the Thevenin‑equivalent expression for \(V_{2}\) with Cramer’s rule  

When the node‑voltage equations of the network are written in matrix form  
\[
\mathbf G\,\mathbf v = \mathbf i_{\text{src}},
\]
the unknown voltage \(V_{2}\) can be isolated with Cramer’s rule.  
The rule tells us that the solution for the second component of \(\mathbf v\) is the
ratio of two determinants:

\[
V_{2}= \frac{\Delta_{1}}{\Delta}\,,
\qquad 
\Delta_{1}= \det\bigl[\; \mathbf G\ \text{with column 2 replaced by the RHS vector}\;\bigr],\;
\Delta = \det(\mathbf G).
\]

### 1.  Dependence of the determinants on the load

* The numerator \(\Delta_{1}\) **does not contain the load conductance** \(G_{L}=1/R_{L}\); therefore \(\Delta_{1}\) is independent of the load resistance.  
* The denominator \(\Delta\) **does contain** \(G_{L}\) because the second column of \(\mathbf G\) includes the term \(G_{L}\).

To make this dependence explicit we rewrite the second column of \(\mathbf G\) as the sum of two columns:

\[
\begin{aligned}
\text{column 2} &= 
\underbrace{\begin{bmatrix}0 \\ G_{2} \\ 0 \\ G_{L} \\ 0\end{bmatrix}}_{\text{load‑free part}}
\;+\;
\underbrace{\begin{bmatrix}0 \\ 0 \\ 0 \\ G_{L} \\ 0\end{bmatrix}}_{\text{pure‑load part}} .
\end{aligned}
\]

Because a determinant is linear in any column, \(\Delta\) can be expressed as the sum of two
determinants:

\[
\Delta = \underbrace{\Delta}_{\text{no }G_{L}} \;+\; G_{L}\,\underbrace{\Delta_{2}}_{\text{independent of }G_{L}} .
\]

Here \(\Delta\) (the first term) contains no appearance of \(G_{L}\), while the second term pulls the factor \(G_{L}\) outside the determinant, leaving a new determinant \(\Delta_{2}\) that again depends only on the fixed circuit elements.

### 2.  Compact form of \(V_{2}\)

Substituting the decomposition of \(\Delta\) into the Cramer expression gives

\[
V_{2}= \frac{\Delta_{1}}{\Delta + G_{L}\,\Delta_{2}} .
\]

All three symbols \(\Delta_{1},\Delta,\Delta_{2}\) are **constants with respect to the load**; they are determined solely by the internal resistances, conductances, and sources of the original network.

### 3.  Open‑circuit voltage \(V_{2}^{\text{OC}}\)

If the load is removed (\(R_{L}\rightarrow\infty\) so that \(G_{L}=0\)), the expression reduces to

\[
V_{2}^{\text{OC}} = \frac{\Delta_{1}}{\Delta}.
\]

Thus the open‑circuit voltage is simply the ratio of the two load‑independent determinants.

### 4.  Introducing the Thevenin resistance

Dividing numerator and denominator of the general expression by \(\Delta\) yields

\[
V_{2}= 
\frac{\displaystyle\frac{\Delta_{1}}{\Delta}}
     {\,1 + G_{L}\,\frac{\Delta_{2}}{\Delta}\,}
   = \frac{V_{2}^{\text{OC}}}{1 + G_{L} R_{\text{TH}}}\!,
\]
where we have defined the **Thevenin resistance**

\[
\boxed{ R_{\text{TH}} \;=\; \frac{\Delta_{2}}{\Delta} } .
\]

Because \(\Delta_{2}\) and \(\Delta\) have the same physical units (ohms‑siemens in the denominator), their ratio indeed carries the units of resistance, as a quick dimensional check confirms.

Since \(G_{L}=1/R_{L}\), the denominator can be rewritten:

\[
1 + G_{L}R_{\text{TH}} = 1 + \frac{R_{\text{TH}}}{R_{L}}
                     = \frac{R_{L}+R_{\text{TH}}}{R_{L}} .
\]

Multiplying numerator and denominator by \(R_{L}\) gives the familiar voltage‑division form

\[
\boxed{ V_{2}= \frac{R_{L}}{R_{L}+R_{\text{TH}}}\; V_{2}^{\text{OC}} } .
\]

### 5.  Interpretation as a Thevenin equivalent

The result shows that the original network, as seen from the terminals where \(V_{2}\) is measured, can be replaced by a **Thevenin equivalent circuit**:

* a single voltage source \(V_{\text{TH}} = V_{2}^{\text{OC}}\);
* in series with a resistance \(R_{\text{

**Diagrams/board content from this segment:**

![Thevenin Ri 5 Rev Ve can be found using Cramer's rule: Ve = (captured at 370.0s)](extracted_images/video_test2_full/frame_370.0s.png)
*Thevenin Ri 5 Rev Ve can be found using Cramer's rule: Ve = (captured at 370.0s)*

![az Ov nev Va can be found using Cramer's rule: Ve = Gs dex(6 (captured at 445.0s)](extracted_images/video_test2_full/frame_445.0s.png)
*az Ov nev Va can be found using Cramer's rule: Ve = Gs dex(6 (captured at 445.0s)*


---

## Thevenin Equivalent Circuit – Finding \(V_{\text{TH}}\) and \(R_{\text{TH}}\)

When a linear network contains resistors, independent voltage or current sources, and possibly dependent sources, **Thevenin’s theorem** guarantees that the entire network, as viewed from any pair of terminals \(A\) and \(B\), can be replaced by a single voltage source \(V_{\text{TH}}\) in series with a single resistance \(R_{\text{TH}}\).  

The simplified model behaves identically to the original network for **any** load resistance \(R_{\!L}\) connected across \(A\)–\(B\). Consequently the voltage across, or the current through, \(R_{\!L\!}\) is the same whether the load is attached to the original circuit or to its Thevenin equivalent.

---

### 1. Determining the Thevenin Voltage \(V_{\text{TH}}\)

Because the two circuits are equivalent, the **open‑circuit voltage** measured between the terminals must be identical.  

1. **Leave the terminals A–B disconnected** (no load).  
2. **Measure the voltage** that appears across them; denote this open‑circuit voltage by \(V_{\!OC}\).  
3. By definition of the Thevenin model, when the load is removed there is no current through \(R_{\text{TH}}\); therefore no voltage drop occurs across \(R_{\text{TH}}\). The entire terminal voltage is then the source voltage of the equivalent circuit:

\[
V_{\text{TH}} = V_{\!OC}.
\]

Thus the Thevenin voltage is simply the open‑circuit voltage of the original network.

---

### 2. Determining the Thevenin Resistance \(R_{\text{TH}}\)

Two complementary techniques are commonly used.

#### Method 1 – Deactivate All Independent Sources  

1. **Turn off every independent source** while leaving dependent sources untouched:  
   * An independent voltage source is replaced by a short circuit.  
   * An independent current source is replaced by an open circuit.  
2. **Look into the terminals A–B** of the now‑passive network.  
3. The resistance seen looking into the ports is the Thevenin resistance:

\[
R_{\text{TH}} = \left. \text{Resistance seen between } A \text{ and } B \right|_{\text{indep. sources off}} .
\]

If the resulting network is simple enough, the resistance can be read directly by inspection.  
When inspection is impractical, a **test source** can be inserted:

* **Test‑voltage method** – apply a known voltage \(V_{\!test}\) across A–B, measure the resulting current \(I_{\!test}\), then  

  \[
  R_{\text{TH}} = \frac{V_{\!test}}{I_{\!test}}.
  \]

* **Test‑current method** – inject a known current \(I_{\!test}\) into the terminals, measure the resulting voltage \(V_{\!test}\), and compute  

  \[
  R_{\text{TH}} = \frac{V_{\!test}}{I_{\!test}}.
  \]

Both approaches rely on the fact that, with all independent sources nulled, the network behaves as a pure linear resistor seen from the terminals.

#### Method 2 – Use Open‑Circuit Voltage and Short‑Circuit Current  

1. **Find the open‑circuit voltage** \(V_{\!OC}\) (already obtained as \(V_{\text{TH}}\)).  
2. **Short the terminals** A–B together, creating a zero‑resistance connection, and compute the resulting current that flows from the source into the short. Call this current \(I_{\!SC}\).  
3. Because the Thevenin model reduces to a voltage source \(V_{\text{TH}}\) feeding a short, the current through the short is simply  

\[
I_{\!SC}= \frac{V_{\text{TH}}}{R_{\text{TH}}}.
\]

4. Rearranging gives the Thevenin resistance directly:

\[
R_{\text{TH}} = \frac{V_{\!OC}}{I_{\!SC}}.
\]

Both methods must yield the same \(R_{\text{TH}}\); the choice depends on which is more convenient for the particular circuit.

---

### 3. Why the Load Sees No Difference

When the load \(R_{\!L}\) is attached to the original network, the terminal voltage is

\[
V_{L}= V_{\text{TH}}\,\frac{R_{\!L}}{R_{\text{TH}}+R_{\!L}}.
\]

Replacing the original network with its Thevenin equivalent yields exactly the same expression, because the series combination of \(V_{\text{TH}}\) and \(R_{\text{TH}}\) reproduces the same voltage division. Hence the **current through** and **voltage across** any load are preserved, which is the practical power of Thevenin’s theorem.

---

### 4. Quick Summary of the Procedure

| Goal | Procedure |
|------|-----------|
| **Find \(V_{\text{TH}}\)** | Measure the open‑circuit voltage \(V_{\!OC}\) across the terminals. |
| **Find \(R_{\text{TH}}\) – Method 1** | Deactivate all independent sources; compute resistance seen between the terminals, optionally using a test source (\(R_{\text{TH}} = V_{\!test}/I_{\!test}\)). |
| **Find \(R_{\text{TH}}\) – Method 2** | Determine \(V_{\!OC}\) and the short‑circuit current \(I_{\!SC}\); then \(R_{\

**Diagrams/board content from this segment:**

![Rr Circuit A A (resistors, ‘ sources, Vm Cevs, Coes, vevs, v (captured at 765.0s)](extracted_images/video_test2_full/frame_765.0s.png)
*Rr Circuit A A (resistors, ‘ sources, Vm Cevs, Coes, vevs, v (captured at 765.0s)*


---

## Determining the Thevenin Equivalent by Open‑Circuit Voltage and Short‑Circuit Current  

When a linear two‑terminal network is replaced by its Thevenin equivalent, the two parameters that must be found are the open‑circuit voltage \(V_{\text{OC}}\) (which is the same as the Thevenin voltage \(V_{\text{TH}}\)) and the short‑circuit current \(I_{\text{SC}}\) (which the instructor called \(I_{\text{AC}}\)).  
Because the short‑circuit current flows through only the Thevenin resistance, Ohm’s law gives a very convenient relationship  

\[
I_{\text{SC}}=\frac{V_{\text{TH}}}{R_{\text{TH}}}\; .
\]

Since \(V_{\text{TH}}=V_{\text{OC}}\), the resistance can be isolated as  

\[
\boxed{R_{\text{TH}}=\frac{V_{\text{OC}}}{I_{\text{SC}}}} .
\]

The practical procedure therefore is:

1. **Leave all independent sources active** and remove the load.  
   *Measure the voltage across the open terminals – this is \(V_{\text{OC}}\).*  
2. **Short

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

## Determining a Thevenin Equivalent with the Graphical (I‑V) Method  

To replace a complicated linear network by its Thevenin equivalent we must find two quantities: the open‑circuit voltage \(V_{\text{OC}}\) (which becomes the Thevenin voltage \(V_{\text{TH}}\)) and the Thevenin resistance \(R_{\text{TH}}\).  
In the example under discussion the original circuit contains two series branches, one of \(12\;\Omega\) and the other of \(4\;\Omega\), across a \(48\;\text{V}\) source.  

### 1. Computing the open‑circuit voltage  

Using the voltage‑division rule,
\[
V_{CB}= \frac{12\;\Omega}{12\;\Omega+4\;\Omega}\times 48\;\text{V}= \frac{12}{16}\times48=36\;\text{V}.
\]
The voltage across the other branch (labelled \(V_{AC}\)) had already been found as
\[
V_{AC}= I\cdot R = 6\;\text{A}\times4\;\Omega = 24\;\text{V}.
\]
Adding the two contributions gives the total voltage between terminals \(A\) and \(B\):
\[
V_{AB}= V_{AC}+V_{CB}=24\;\text{V}+36\;\text{V}=60\;\text{V}.
\]
Thus the open‑circuit voltage is \(V_{\text{OC}}=60\;\text{V}\); this is also the Thevenin voltage,
\[
V_{\text{TH}} = 60\;\text{V}.
\]

### 2. Determining the Thevenin resistance graphically  

The graphical method exploits the linear relationship between the current \(I\) supplied by a test source and the test voltage \(V\) applied across the terminals:

\[
I = \frac{V_{\text{TH}}-V}{R_{\text{TH}}}.
\]

This equation describes a straight line with **negative slope** \(-1/R_{\text{TH}}\).  

- **X‑intercept (voltage axis).** Set \(I=0\) and solve for \(V\):
  \[
  V = V_{\text{TH}}.
  \]
  Hence the point where the line meets the voltage axis directly reads the open‑circuit voltage, \(60\;\text{V}\) in our case.

- **Y‑intercept (current axis).** Set \(V=0\) and obtain
  \[
  I = \frac{V_{\text{TH}}}{R_{\text{TH}}}=I_{\text{SC}},
  \]
  the short‑circuit current that would flow if the terminals were connected by an ideal wire.  

From the simulated I‑V plot the Y‑intercept is measured as \(I_{\text{SC}} = 8.57\;\text{A}\). Using the relationship
\[
R_{\text{TH}} = \frac{V_{\text{TH}}}{I_{\text{SC}}}
          = \frac{60\;\text{V}}{8.57\;\text{A}}
          \approx 7\;\Omega,
\]
we recover the Thevenin resistance that was previously obtained by algebraic reduction.

### 3. Practical ways to obtain the plot  

Two equivalent experimental (or simulation) procedures generate the same straight line:

1. **Apply a variable voltage source** between the terminals and record the resulting current. Plot \(I\) versus the applied voltage \(V\).  
2. **Connect a variable load resistor** \(R_{\text{L}}\) across the terminals, vary its value, and plot the measured load current against the load voltage. The points again lie on the same line because the underlying relation \(I = (V_{\text{TH}}-V)/R_{\text{TH}}\) holds irrespective of whether the excitation is a source or a resistor.

Both approaches produce an identical intercept pair \((V_{\text{OC}}, I_{\text{SC}})\) and therefore the same Thevenin parameters.

### 4. Summary of the example  

| Quantity | Value | How obtained |
|----------|-------|--------------|
| Open‑circuit voltage \(V_{\text{OC}}\) (or \(V_{\text{TH}}\)) | \(60\;\text{V}\) | Voltage‑division calculation and X‑intercept of the I‑V plot |
| Short‑circuit current \(I_{\text{SC}}\) | \(8.57\;\text{A}\) | Y‑intercept of the I‑V plot |
| Thevenin resistance \(R_{\text{TH}}\) | \(\approx 7\;\Omega\) | \(R_{\text{TH}} = V_{\text{TH}}/I_{\text{SC}}\) or slope \(-1/R_{\text{TH}}\) of the line |

The graphical method thus offers a quick visual confirmation of the Thevenin equivalent. Once \(V_{\text{TH}}\) and \(R_{\text{TH}}\) are known, any load connected to the terminals can be analyzed instantly by treating the network as a simple series combination of a voltage source and a resistor—an insight that underpins the analysis of RC circuits, amplifiers, and many other practical systems.

**Diagrams/board content from this segment:**

![for finding Bo Vn, vn Ov ‘ Vn = v 1= ~T— (Note: negative slo (captured at 1505.0s)](extracted_images/video_test2_full/frame_1505.0s.png)
*for finding Bo Vn, vn Ov ‘ Vn = v 1= ~T— (Note: negative slo (captured at 1505.0s)*

![49 40 20 4 120 20 © 8 (captured at 1660.0s)](extracted_images/video_test2_full/frame_1660.0s.png)
*49 40 20 4 120 20 © 8 (captured at 1660.0s)*
