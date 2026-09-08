# new lecture  

**Introduction** – This chapter presents Thevenin’s theorem, which guarantees that any linear bilateral network can be replaced by an equivalent voltage source $V_{\text{TH}}$ in series with a resistance $R_{\text{TH}}$.  We first prove why such an equivalent must exist, then show how to obtain the Thevenin parameters algebraically (node‑voltage analysis and Cramer’s rule) and practically (open‑circuit/short‑circuit measurements, source‑deactivation, and the graphical I–V method).  Throughout, the same numerical example is used to illustrate each technique.

---

## 1. Statement of Thevenin’s Theorem  

**Theorem 1 (Thevenin).** *Any linear bilateral network observed from a pair of terminals can be replaced by a single ideal voltage source $V_{\text{th}}$ in series with a resistance $R_{\text{th}}$.*  

The two parameters $V_{\text{th}}$ (Thevenin voltage) and $R_{\text{th}}$ (Thevenin resistance) are completely determined by the elements that lie inside the network; the external load experiences exactly the same voltage‑current relationship whether the original circuit or its Thevenin equivalent is connected.

---

## 2. Why an Equivalent Exists  

A linear circuit obeys the superposition principle, so the terminal voltage $V$ is an affine function of the load current $I_{L}$:

$$
V = V_{\text{oc}} - I_{L}\,R_{\text{eq}} .
$$

Here $V_{\text{oc}}$ is the **open‑circuit voltage** (the voltage measured when $I_{L}=0$) and the slope $-R_{\text{eq}}$ is independent of the load because the internal resistance of a linear network does not change with external connection.  Rearranging gives the familiar series‑source form

$$
V = V_{\text{th}} - I_{L}R_{\text{th}}, \qquad 
\text{with } V_{\text{th}} = V_{\text{oc}},\; R_{\text{th}} = R_{\text{eq}} .
$$

Thus any linear network can be collapsed to a Thevenin source that reproduces exactly the same $V\!-\!I_{L}$ line.

---

## 3. Algebraic Determination of the Thevenin Parameters  

### 3.1 Example Network  

Consider the circuit shown below (load resistor $R_{L}$ connected across terminals $A$–$B$). The goal is to express the voltage $V$ across $R_{L}$ in terms of the surrounding resistors and the independent current source $I_{0}$.

### 3.2 Node‑Voltage Formulation  

1. **Choose a reference node** at the bottom of the diagram (ground).  
2. **Define node voltages**

\[
\begin{aligned}
V_{1}&=\text{voltage at node }A,\\
V_{2}&=\text{voltage at node }B\;(=0\text{ V for the reference}),\\
V_{3}&=\text{voltage at node }C .
\end{aligned}
\]

3. **Introduce conductances** for algebraic convenience  

\[
G_{1}= \frac{1}{R_{1}},\qquad 
G_{2}= \frac{1}{R_{2}},\qquad 
G_{3}= \frac{1}{R_{3}},\;\dots
\]

so that a current through a resistor is $G\,(V_{\text{high}}-V_{\text{low}})$.

4. **Apply Kirchhoff’s Current Law (KCL)** taking currents **leaving** a node as positive.

*Node A*

\[
G_{1}(V_{1}-V_{3}) + G_{2}(V_{1}-V_{2}) - I_{0}=0 .
\tag{1}
\]

*Node B*

\[
G_{2}(V_{2}-V_{1}) + G_{3}(V_{2}-V_{3})=0 .
\tag{2}
\]

*Node C*

\[
G_{1}(V_{3}-V_{1}) + G_{3}(V_{3}-V_{2}) + I_{0}=0 .
\tag{3}
\]

5. **Collect the equations in matrix form**

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

![](extracted_images/video_test2_full/frame_5.0s.png)  
*~ NPTEL (captured at 5.0s)*  

![](extracted_images/video_test2_full/frame_10.0s.png)  
*BASIC ELECTRONICS mst - (captured at 10.0s)*  

![](extracted_images/video_test2_full/frame_60.0s.png)  
*The, Re Oe R ‘ oN How is V related tothe circuit parameters? (captured at 60.0s)*  

### 3.3 Solving for $V_{2}$ with Cramer’s Rule  

The matrix equation $\mathbf{G}\mathbf{V} = \mathbf{I}_{s}$ can be solved for the second component $V_{2}$ by Cramer’s rule:

\[
V_{2}= \frac{\Delta_{1}}{\Delta},
\qquad
\Delta_{1}= \det\bigl[\mathbf{G}\ \text{with column 2 replaced by }\mathbf{I}_{s}\bigr],
\qquad
\Delta = \det(\mathbf{G}).
\]

#### Load dependence  

* The numerator $\Delta_{1}$ does **not** contain the load conductance $G_{L}=1/R_{L}$; therefore $\Delta_{1}$ is independent of the load.  
* The denominator $\Delta$ **does** contain $G_{L}$ because the second column of $\mathbf{G}$ includes the term $G_{L}$.

Writing the second column as the sum of a load‑free part and a pure‑load part makes the dependence explicit:

\[
\text{column 2}= 
\underbrace{\begin{bmatrix}0 \\ G_{2} \\ 0 \\ G_{L} \\ 0\end{bmatrix}}_{\text{load‑free}} 
+ 
\underbrace{\begin{bmatrix}0 \\ 0 \\ 0 \\ G_{L} \\ 0\end{bmatrix}}_{\text{pure‑load}} .
\]

Since a determinant is linear in any column,

\[
\Delta = \underbrace{\Delta}_{\text{no }G_{L}} \;+\; G_{L}\,\underbrace{\Delta_{2}}_{\text{independent of }G_{L}} .
\]

All three symbols $\Delta_{1},\Delta,\Delta_{2}$ are constants with respect to the load.

#### Compact expression  

Substituting the decomposition of $\Delta$ gives

\[
V_{2}= \frac{\Delta_{1}}{\Delta + G_{L}\,\Delta_{2}} .
\]

When the load is removed ($G_{L}=0$) we obtain the **open‑circuit voltage**

\[
V_{2}^{\text{OC}} = \frac{\Delta_{1}}{\Delta}.
\]

Dividing numerator and denominator of the general expression by $\Delta$ yields

\[
V_{2}= 
\frac{V_{2}^{\text{OC}}}{1 + G_{L}R_{\text{TH}}},\qquad 
R_{\text{TH}} \equiv \frac{\Delta_{2}}{\Delta}.
\]

Because $G_{L}=1/R_{L}$, the denominator becomes

\[
1 + G_{L}R_{\text{TH}} = 1 + \frac{R_{\text{TH}}}{R_{L}}
                     = \frac{R_{L}+R_{\text{TH}}}{R_{L}} ,
\]

and after multiplying top and bottom by $R_{L}$ we recover the familiar voltage‑division form

\[
\boxed{ V_{2}= \frac{R_{L}}{R_{L}+R_{\text{TH}}}\; V_{2}^{\text{OC}} } .
\]

![](extracted_images/video_test2_full/frame_370.0s.png)  
*Thevenin Ri 5 Rev Ve can be found using Cramer's rule: Ve = (captured at 370.0s)*  

![](extracted_images/video_test2_full/frame_445.0s.png)  
*az Ov nev Va can be found using Cramer's rule: Ve = Gs dex(6 (captured at 445.0s)*  

Thus the original network, as viewed from the terminals where $V_{2}$ is measured, is equivalent to a voltage source $V_{\text{TH}} = V_{2}^{\text{OC}}$ in series with a resistance $R_{\text{TH}}$.

---

## 4. Practical Determination of $V_{\text{TH}}$ and $R_{\text{TH}}$

### 4.1 Open‑Circuit Voltage  

Because the Thevenin and original circuits are equivalent, the **open‑circuit voltage** measured across the terminals equals the Thevenin voltage:

1. Disconnect any load from terminals $A$–$B$.  
2. Measure the voltage that appears; denote it $V_{\!OC}$.  

\[
V_{\text{TH}} = V_{\!OC}.
\]

### 4.2 Thevenin Resistance – Two Complementary Methods  

#### Method 1: Deactivate Independent Sources  

* Replace each independent voltage source by a short circuit.  
* Replace each independent current source by an open circuit.  
* Leave dependent sources untouched.  

The resistance seen looking into the terminals is $R_{\text{TH}}$.  When the reduced network is simple, $R_{\text{TH}}$ can be read directly; otherwise a test source may be used:

* **Test‑voltage method** – apply a known voltage $V_{\!test}$ across $A$–$B$, measure the resulting current $I_{\!test}$, then  

\[
R_{\text{TH}} = \frac{V_{\!test}}{I_{\!test}} .
\]

* **Test‑current method** – inject a known current $I_{\!test}$, measure the resulting voltage $V_{\!test}$, and compute  

\[
R_{\text{TH}} = \frac{V_{\!test}}{I_{\!test}} .
\]

#### Method 2: Open‑Circuit Voltage and Short‑Circuit Current  

1. Determine $V_{\!OC}$ as above.  
2. Short the terminals ($A$–$B$) together and compute the current that flows, $I_{\!SC}$.  

Because the Thevenin model reduces to a source $V_{\text{TH}}$ feeding a short,  

\[
I_{\!SC}= \frac{V_{\text{TH}}}{R_{\text{TH}}}\; \Longrightarrow\;
R_{\text{TH}} = \frac{V_{\!OC}}{I_{\!SC}} .
\]

Both methods must give the same $R_{\text{TH}}$; the choice depends on which is more convenient for the circuit at hand.

![](extracted_images/video_test2_full/frame_765.0s.png)  
*Rr Circuit A A (resistors, ‘ sources, Vm Cevs, Coes, vevs, v (captured at 765.0s)*  

### 4.3 Verification via Load Voltage  

When a load $R_{L}$ is attached, the terminal voltage predicted by the Thevenin model is

\[
V_{L}= V_{\text{TH}}\;\frac{R_{L}}{R_{\text{TH}}+R_{L}} .
\]

Because the model reproduces exactly the same voltage division as the original network, the current through and voltage across any load are preserved.

---

## 5. Graphical (I‑V) Method for Determining the Thevenin Equivalent  

A linear network exhibits a straight‑line relationship between the current $I$ supplied by a test source and the test voltage $V$ applied across the terminals:

\[
I = \frac{V_{\text{TH}}-V}{R_{\text{TH}}}.
\]

The line has a **negative slope** $-1/R_{\text{TH}}$ and two useful intercepts.

* **X‑intercept (voltage axis):** set $I=0$ ⇒ $V = V_{\text{TH}}$ (the open‑circuit voltage).  
* **Y‑intercept (current axis):** set $V=0$ ⇒ $I = I_{\!SC}=V_{\text{TH}}/R_{\text{TH}}$ (the short‑circuit current).

### 5.1 Example  

The original circuit contains two series branches, $12\;\Omega$ and $4\;\Omega$, across a $48\;\text{V}$ source.

*Open‑circuit voltage* (by voltage division)

\[
V_{CB}= \frac{12\;\Omega}{12\;\Omega+4\;\Omega}\,48\;\text{V}
      = \frac{12}{16}\times48 = 36\;\text{V}.
\]

The other branch yields $V_{AC}= I\cdot R = 6\;\text{A}\times4\;\Omega = 24\;\text{V}$, so

\[
V_{\!OC}=V_{AB}=V_{AC}+V_{CB}=24\;\text{V}+36\;\text{V}=60\;\text{V}.
\]

Thus $V_{\text{TH}} = 60\;\text{V}$.

*Short‑circuit current* obtained from the I–V plot (Y‑intercept) is $I_{\!SC}=8.57\;\text{A}$, giving

\[
R_{\text{TH}} = \frac{V_{\text{TH}}}{I_{\!SC}}
               = \frac{60\;\text{V}}{8.57\;\text{A}}
               \approx 7\;\Omega .
\]

The same line can be generated either by sweeping a variable voltage source across the terminals and recording the current, or by attaching a variable load resistor $R_{L}$, measuring $(V,I)$ pairs, and plotting $I$ versus $V$.

![](extracted_images/video_test2_full/frame_1505.0s.png)  
*for finding Bo Vn, vn Ov ‘ Vn = v 1= ~T— (Note: negative slo (captured at 1505.0s)*  

![](extracted_images/video_test2_full/frame_1660.0s.png)  
*49 40 20 4 120 20 © 8 (captured at 1660.0s)*  

### 5.2 Summary of the Example  

| Quantity | Value | Obtained from |
|----------|-------|----------------|
| $V_{\text{TH}}$ (open‑circuit voltage) | $60\;\text{V}$ | Voltage‑division calculation / X‑intercept |
| $I_{\text{SC}}$ (short‑circuit current) | $8.57\;\text{A}$ | Y‑intercept of the I‑V plot |
| $R_{\text{TH}}$ | $\approx 7\;\Omega$ | $R_{\text{TH}} = V_{\text{TH}}/I_{\text{SC}}$ or slope $-1/R_{\text{TH}}$ |

The graphical method therefore provides a quick visual confirmation of the Thevenin equivalent and can be used when analytical reduction is cumbersome.

---

## 6. Closing Summary – Key Takeaways  

- **Thevenin’s theorem** guarantees that any linear bilateral network can be replaced by a single voltage source $V_{\text{TH}}$ in series with a resistance $R_{\text{TH}}$, preserving all terminal $V$–$I$ characteristics.  
- **Open‑circuit voltage** $V_{\!OC}$ measured at the terminals equals the Thevenin voltage: $V_{\text{TH}} = V_{\!OC}$.  
- **Thevenin resistance** can be obtained either by (a) deactivating independent sources and measuring the input resistance, or (b) using the ratio $R_{\text{TH}} = V_{\!OC}/I_{\!SC}$ where $I_{\!SC}$ is the short‑circuit current.  
- **Cramer’s rule** applied to the node‑voltage matrix yields a compact expression $V = \dfrac{R_{L}}{R_{L}+R_{\text{TH}}}\,V_{\text{TH}}$, confirming the voltage‑division interpretation of the equivalent circuit.  
- **Graphical I–V method** exploits the linear relationship $I = (V_{\text{TH}}-V)/R_{\text{TH}}$; the X‑intercept gives $V_{\text{TH}}$, the Y‑intercept gives $I_{\text{SC}}$, and the slope provides $R_{\text{TH}}$.