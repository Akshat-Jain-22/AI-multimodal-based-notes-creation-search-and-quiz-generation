# ABCD

## Thevenin’s Theorem – From Circuit Description to Equivalent Parameters  

The Thevenin theorem states that **any linear, bilateral network seen from two terminals can be replaced by a single voltage source \(V_{\text{Th}}\) in series with a resistance \(R_{\text{Th}}\)**, without altering the voltage‑current relationship at those terminals.  This simplification is invaluable because it reduces a potentially complex web of resistors, sources, and dependent elements to a pair of easily handled parameters.  

### 1.  Why a Thevenin Equivalent Exists  

Consider a circuit that drives a load resistor \(R_{L}\).  The quantity of interest is the voltage \(V\) across \(R_{L}\).  If we write the node voltages of the original network (with respect to a chosen reference node) and express all currents leaving each node, the algebraic relationships are linear.  Linear systems have the property that the response at any port (here the two terminals of \(R_{L}\)) can be expressed as a **linear function of the source excitations**.  Consequently the whole network behaves exactly like a single source and a series resistance when viewed from those terminals.  

### 2.  Formulating the Problem with Node‑Voltage Analysis  

To make the linear relationship explicit we label the important nodes:

| Node | Symbol | Meaning |
|------|--------|---------|
| Reference (ground) | – | Voltage defined as 0 V |
| Node A | \(V_{1}\) | Voltage at the first interior node |
| Node B | \(V_{2}\) | Voltage at the second interior node (the node directly connected to the load) |
| Node C | \(V_{3}\) | Voltage at the third interior node |

The circuit also contains resistors \(R_{1},R_{2},\dots\) and a current source \(I_{0}\) that injects current into node A.  For compactness we introduce conductances  

\[
G_{1} = \frac{1}{R_{1}},\qquad 
G_{2} = \frac{1}{R_{2}},\qquad \dots
\]

Writing Kirchhoff’s Current Law (KCL) with the **convention “current leaving the node is positive”** gives a set of linear equations.  At node A the three currents are  

* \( (V_{1}-V_{3})/R_{1} = G_{1}(V_{1}-V_{3})\) – leaving toward node C,  
* \( (V_{1}-V_{2})/R_{2} = G_{2}(V_{1}-V_{2})\) – leaving toward node B,  
* \(-I_{0}\) – the external source injects current, thus it appears as a negative term because it enters the node.

Summing these currents to zero yields  

\[
G_{1}(V_{1}-V_{3}) + G_{2}(V_{1}-V_{2}) - I_{0}=0 .
\]

Repeating the same procedure for nodes B and C produces two additional equations of identical form, each involving the appropriate conductances and node voltages.

### 3.  Matrix Representation  

Collecting the three KCL equations we obtain a compact matrix equation  

\[
\underbrace{\begin{bmatrix}
G_{1}+G_{2} & -G_{2} & -G_{1}\\[4pt]
-G_{2} & G_{2}+G_{3} & -G_{3}\\[4pt]
-G_{1} & -G_{3} & G_{1}+G_{3}
\end{bmatrix}}_{\displaystyle \mathbf{G}}
\begin{bmatrix}
V_{1}\\ V_{2}\\ V_{3}
\end{bmatrix}
=
\underbrace{\begin{bmatrix}
I_{0}\\ 0\\ 0
\end{bmatrix}}_{\displaystyle \mathbf{I}_{s}} .
\]

Here  

* \(\mathbf{G}\) is the **conductance matrix** (the “admittance” analogue of the resistance matrix),  
* \(\mathbf{V}\) is the column vector of node voltages, and  
* \(\mathbf{I}_{s}\) is the source‑current vector, containing the only independent excitation \(I_{0}\).  

The objective is to find the voltage at node B, \(V_{2}\), because the load voltage \(V\) is exactly \(V_{2}\) when the reference node is grounded.

### 4.  Solving for the Desired Node Voltage  

Because the system is linear, any standard linear‑algebra technique can be used.  The lecture illustrates **Cramer's rule**, which expresses a particular unknown as the ratio of two determinants:

\[
V_{2}= \frac{D_{1}}{D_{2}} .
\]

* \(D_{2}\) is the determinant of the original conductance matrix \(\mathbf{G}\).  
* \(D_{1}\) is the determinant of the same matrix after **replacing the second column** (the column that multiplies \(V_{2}\)) with the source‑current vector \(\mathbf{I}_{s}\).

Carrying out the determinant calculations (the algebra is routine but lengthy) yields an explicit expression for \(V_{2}\) in terms of the conductances \(G_{i}\) and the source current \(I_{0}\).  This expression is the **Thevenin voltage** seen by the load, because it is the open‑circuit voltage that would appear across the terminals when \(R_{L}\) is removed.

### 5.  Extracting Thevenin Parameters  

Once the open‑circuit voltage \(V_{\text{Th}} = V_{2}\) is known, the **Thevenin resistance** \(R_{\text{Th}}\) can be obtained by a second, simpler experiment:

1. **Deactivate all independent sources** (replace voltage sources by short circuits and current sources by open circuits).  
2. **Calculate the resistance looking into the terminals**; this is exactly \(R_{\text{Th}}\).  

Because the conductance matrix already embodies the resistive network, deactivating the sources simply removes the \(\mathbf{I}_{s}\) vector, leaving the homogeneous system \(\mathbf{G}\mathbf{V}=0\).  Solving for the ratio of the resulting terminal voltage to a test current yields \(R

**Diagrams/board content from this segment:**

![~ NPTEL (captured at 5.0s)](D:/Documents/classroom-notes - Copy/scripts/pipeline_runs/abcd/extracted_images/video_test2_full/frame_5.0s.png)
*This image is a title slide for an NPTEL course titled "BASIC ELECTRONICS." It features the NPTEL logo on the left and the Indian Institute of Technology (IIT) logo on the right, set against a dark blue background with a digital network pattern. The bottom half of the image is blank white space.*

![BASIC ELECTRONICS mst - (captured at 10.0s)](D:/Documents/classroom-notes - Copy/scripts/pipeline_runs/abcd/extracted_images/video_test2_full/frame_10.0s.png)
*This is a title slide for a lecture series titled "BASIC ELECTRONICS" presented by Prof. Mahesh Patil from IIT Bombay. The slide features a dark blue background with an abstract network graphic of connected nodes and lines, overlaid with white text. The bottom half of the image is blank white space.*

![The, Re Oe R ‘ oN How is V related tothe circuit parameters? (captured at 60.0s)](D:/Documents/classroom-notes - Copy/scripts/pipeline_runs/abcd/extracted_images/video_test2_full/frame_60.0s.png)
*This image shows a circuit diagram used to illustrate Thevenin's theorem, featuring a current source $I_0$ in parallel with resistor $R_1$, which is then connected in series with resistors $R_2$, $R_4$, and $R_3$. The voltage $V$ is defined across the load resistor $R_4$ on the right side of the circuit. The slide poses the question "How is $V$ related to the circuit parameters?" to prompt the derivation of the output voltage.*


---

## Deriving the Thevenin Equivalent for \(V_2\) with Cramer’s Rule  

In order to express the node voltage \(V_2\) in a form that reveals the Thevenin equivalent seen from the load, we start from the linear system that describes the circuit.  The conductance matrix (often called the **G‑matrix**) relates the node voltages to the independent sources.  Applying **Cramer’s rule** to solve for the second node voltage gives  

\[
V_2=\frac{\Delta_1}{\Delta},
\]

where  

* \(\Delta\) is the determinant of the original G‑matrix, and  
* \(\Delta_1\) is the determinant of the same matrix after **replacing its second column** with the right‑hand‑side (RHS) source vector.

### 1.  What the determinants contain  

A careful inspection of the matrices shows that  

* \(\Delta_1\) **does not contain the load conductance** \(G_L\) (or equivalently the load resistance \(R_L\)).  Hence \(\Delta_1\) is a constant that depends only on the internal elements of the network (source resistances, internal conductances, etc.).  

* \(\Delta\), on the other hand, **does contain \(G_L\)** because the load appears in the second column of the original G‑matrix.  By writing that column as the sum of two simpler columns—one that is independent of \(G_L\) and one that is proportional to \(G_L\)—the determinant can be split into two parts:

\[
\Delta = \underbrace{\Delta}_{\text{no }G_L} \;+\; G_L \underbrace{\Delta_2}_{\text{no }G_L},
\]

where \(\Delta_2\) is the determinant of the matrix obtained after factoring the \(G_L\) term out of the column.  By construction, \(\Delta_2\) also contains no load parameter.

Consequently the exact expression for \(V_2\) becomes  

\[
V_2=\frac{\Delta_1}{\Delta + G_L\Delta_2}.
\tag{1}
\]

All three symbols \(\Delta_1,\;\Delta,\;\Delta_2\) are **independent of the load**; only the explicit factor \(G_L\) introduces load dependence.

### 2.  From conductance to resistance form  

Since \(G_L = 1/R_L\), we rewrite (1) as  

\[
V_2 = \frac{\Delta_1}{\Delta + \frac{\Delta_2}{R_L}}
      = \frac{\displaystyle\frac{\Delta_1}{\Delta}}
             {1 + \frac{\Delta_2}{\Delta}\,\frac{1}{R_L}} .
\]

Define two convenient load‑independent quantities:

* **Open‑circuit voltage** (the voltage at node 2 when the load is removed):
  \[
  V_{2,\text{OC}} \;=\; \frac{\Delta_1}{\Delta}.
  \]

* **Thevenin resistance** seen by the load:
  \[
  R_{\text{Th}} \;=\; \frac{\Delta_2}{\Delta}.
  \]

Both have the expected units—\(V_{2,\text{OC}}\) is a voltage, \(R_{\text{Th}}\) is a resistance.  Substituting these definitions gives a compact, physically transparent formula:

\[
V_2 = \frac{V_{2,\text{OC}}}{1 + \dfrac{R_{\text{Th}}}{R_L}}
    = \frac{R_L}{R_L + R_{\text{Th}}}\;V_{2,\text{OC}} .
\tag{2}
\]

### 3.  Interpretation  

Equation (2) is precisely the **voltage‑division law** for a source of open‑circuit voltage \(V_{2,\text{OC}}\) in series with its Thevenin resistance \(R_{\text{Th}}\).  The original, possibly complicated network has thus been reduced to an equivalent two‑terminal circuit:

* a single voltage source \(V_{\text{TH}} = V_{2,\text{OC}}\),  
* a single series resistance \(R_{\text{TH}} = R_{\text{Th}}\),

connected to the load \(R_L\).  The voltage that actually appears across the load is the fraction \(R_L/(R_L+R_{\text{TH}})\) of the open‑circuit voltage.

### 4.  Special cases  

* **Open circuit** (\(R_L \to \infty\), \(G_L \to 0\)): the denominator of (1) reduces to \(\Delta\) and (2) yields \(V_2 = V_{2,\text{OC}}\), as expected.  
* **Short circuit** (\(R_L \to 0\)): the term \(R_L/(R_L+R_{\text{TH}})\) tends to zero, so the load

**Diagrams/board content from this segment:**

![Thevenin Ri 5 Rev Ve can be found using Cramer's rule: Ve = (captured at 370.0s)](D:/Documents/classroom-notes - Copy/scripts/pipeline_runs/abcd/extracted_images/video_test2_full/frame_370.0s.png)
*This slide illustrates a circuit analysis problem using nodal analysis and Cramer's rule to solve for the node voltage $V_2$. The circuit diagram features a central current source $I_0$ connected between nodes A and C, with resistors $R_1$, $R_2$, and $R_3$ connecting these nodes to ground and to each other. Below the diagram, a mathematical equation is presented showing the calculation of $V_2$ as the ratio of two determinants involving conductance values ($G_1, G_2, G_3$) and the current source $I_0$.*

![az Ov nev Va can be found using Cramer's rule: Ve = Gs dex(6 (captured at 445.0s)](D:/Documents/classroom-notes - Copy/scripts/pipeline_runs/abcd/extracted_images/video_test2_full/frame_445.0s.png)
*This image displays a circuit diagram and a mathematical derivation for finding the node voltage $V_2$ using Cramer's rule. The circuit features three nodes labeled A ($V_1$), B ($V_2$), and C ($V_3$), containing resistors $R_1, R_2, R_3$, a current source $I_0$, and a load resistor $R_L$ connected to ground. The slide presents the formula for $V_2$ as the ratio of two determinants ($\Delta_1 / \det(\mathbf{G})$) and explicitly expands the determinant of the conductance matrix $\mathbf{G}$ into a sum of two $3 \times 3$ matrices.*


---

## Thevenin Equivalent of a Linear Two‑Terminal Network  

When a linear circuit contains any combination of resistors, independent voltage or current sources, and linear dependent sources, **Thevenin’s theorem** guarantees that the entire network, as seen from two terminals A and B, can be replaced by a much simpler model: a single ideal voltage source \(V_{\text{TH}}\) in series with a single resistance \(R_{\text{TH}}\).  

### Why the Replacement Works  

The original network and its Thevenin equivalent present exactly the same electrical behaviour to anything that is connected across A‑B. Consequently, a load resistance \(R_L\) connected to the original circuit will experience the same voltage across it and the same current through it as if it were connected to the Thevenin model. This equivalence follows because both circuits have identical **open‑circuit voltage** (the voltage measured with the load removed) and identical **short‑circuit current** (the current that would flow if the terminals were forced together).  

### Determining the Thevenin Voltage \(V_{\text{TH}}\)  

1. **Remove the load** – leave terminals A and B open.  
2. **Measure or compute the voltage** that appears across the open terminals.  
   - In the original circuit this voltage is denoted \(V_{\text{OC}}\) (or \(V_{\!OC}\)).  
   - In the Thevenin model there is no current through \(R_{\text{TH}}\), so the entire voltage of the ideal source appears at the terminals.  

Hence  

\[
\boxed{V_{\text{TH}} = V_{\text{OC}}}
\]

The open‑circuit voltage of the original network is therefore the Thevenin voltage of its equivalent.

### Determining the Thevenin Resistance \(R_{\text{TH}}\)

Two complementary procedures are commonly used.

#### Method 1 – Deactivate All Independent Sources  

1. **Turn off every independent source** in the original network:  
   - Replace each independent voltage source with a short circuit.  
   - Replace each independent current source with an open circuit.  
   (Dependent sources are left intact because their values depend on circuit variables.)  
2. **Look into the two terminals** A and B. The resistance that the network now presents is exactly \(R_{\text{TH}}\).  

If the resulting resistance is not obvious by inspection, a **test source** can be introduced:  

- Connect a test voltage source \(V_{\text{test}}\) across A‑B, measure the resulting current \(I_{\text{test}}\), and compute  

  \[
  R_{\text{TH}} = \frac{V_{\text{test}}}{I_{\text{test}}}.
  \]

- Alternatively, insert a test current source \(I_{\text{test}}\) and measure the voltage drop \(V_{\text{test}}\) it produces, giving the same ratio \(R_{\text{TH}} = V_{\text{test}}/I_{\text{test}}\).

#### Method 2 – Use Open‑Circuit Voltage and Short‑Circuit Current  

1. **Find the open‑circuit voltage** \(V_{\text{OC}}\) as described above; this equals \(V_{\text{TH}}\).  
2. **Short the terminals** A and B together and determine the current that flows from A to B; call this the **short‑circuit current** \(I_{\text{SC}}\) (the notes sometimes label it \(I_{\text{AC}}\)).  
3. Apply Ohm’s law to the Thevenin model: with the source \(V_{\text{TH}}\) directly across the short, the current is  

   \[
   I_{\text{SC}} = \frac{V_{\text{TH}}}{R_{\text{TH}}}.
   \]

   Solving for the resistance yields  

   \[
   \boxed{R_{\text{TH}} = \frac{V_{\text{OC}}}{I_{\text{SC}}}}.
   \]

Both methods arrive at the same value for \(R_{\text{TH}}\); the choice depends on which is more convenient for the particular circuit.

### Applying the Thevenin Model  

Once \(V_{\text{TH}}\) and \(R_{\text{TH}}\) have been obtained, the analysis of any load becomes straightforward. For a load resistance \(R_L\) connected across A‑B:

- The voltage across the load is  

  \[
  V_L = V_{\text{TH}} \,\frac{R_L}{R_{\text{TH}} + R_L},
  \]

  which is the familiar voltage‑division formula.  
- The current through the load follows  

  \[
  I_L = \frac{V_{\text{TH}}}{R_{\text{TH}} + R_L}.
  \]

These expressions are algebraically identical to those you would write for the original, possibly complicated, network, but they are far easier to evaluate because the Thevenin circuit contains only one source and one resistance.

### Summary  

Thevenin’s theorem tells us that any linear two‑terminal network can be reduced to an ideal voltage source \(V_{\text{TH}}\) in series with a resistance \(R_{\text{TH}}\). The voltage source value is simply the open‑circuit voltage measured at the terminals, while the series resistance can be found either by deactivating all independent sources and measuring the resulting resistance (or using a test source) or by dividing the open‑circuit voltage by the short‑circuit current. With these two parameters in hand, the behavior of any attached load follows directly from basic series‑circuit analysis.

**Diagrams/board content from this segment:**

![Rr Circuit A A (resistors, ‘ sources, Vm Cevs, Coes, vevs, v (captured at 765.0s)](D:/Documents/classroom-notes - Copy/scripts/pipeline_runs/abcd/extracted_images/video_test2_full/frame_765.0s.png)
*The image illustrates Thevenin's theorem, showing the equivalence between a complex linear circuit and its simplified Thevenin equivalent circuit. On the left, a black box labeled "Circuit" contains resistors, voltage sources, current sources, CCVS, CCCS, VCVS, and VCCS, with terminals A and B. On the right, the equivalent circuit consists of a voltage source $V_{Th}$ in series with a resistor $R_{Th}$, also connected to terminals A and B. The slide is titled "Thevenin's theorem" and is credited to M. B. Patil, IIT Bombay.*


---

## Determining Thevenin Parameters Using Open‑Circuit Voltage and Short‑Circuit Current  

When a linear network is viewed from a pair of terminals (A–B), its behavior can be replaced by a **Thevenin equivalent**: a single voltage source \(V_{\text{TH}}\) in series with a resistance \(R_{\text{TH}}\).  The two quantities are obtained directly from the original circuit without any source deactivation for the voltage, but with source deactivation for the resistance.

### 1.  Relationship between the open‑circuit voltage, short‑circuit current and \(R_{\text{TH}}\)

* With the load disconnected the terminals are **open‑circuit**; the voltage measured is the open‑circuit voltage \(V_{\!OC}\).  
* If the terminals are **short‑circuited**, the current that flows is the short‑circuit current \(I_{\!SC}\).  

Because the Thevenin model contains only the series combination of \(V_{\text{TH}}\) and \(R_{\text{TH}}\),

\[
I_{\!SC}= \frac{V_{\text{TH}}}{R_{\text{TH}}}\qquad\text{and}\qquad V_{\!OC}=V_{\text{TH}} .
\]

Eliminating \(V_{\text{TH}}\) gives a very convenient formula for the Thevenin resistance:

\[
\boxed{R_{\text{TH}}=\frac{V_{\!OC}}{I_{\!SC}} } .
\]

Thus, to characterize any linear network we need only (i) the open‑circuit voltage and (ii) the short‑circuit current measured at the same pair of terminals.

### 2.  Procedure for finding \(V_{\text{TH}}\) and \(R_{\text{TH}}\)

| Step | Action | Reason |
|------|--------|--------|
| 1 | **Remove the load** (if present) and compute the voltage across the terminals. | This voltage is \(V_{\!OC}=V_{\text{TH}}\) because no current flows through \(R_{\text{TH}}\). |
| 2 | **Short the terminals** and compute the current that flows. | The current is the short‑circuit current \(I_{\!SC}=V_{\text{TH}}/R_{\text{TH}}\). |
| 3 | **Form the ratio** \(R_{\text{TH}} = V_{\!OC}/I_{\!SC}\). | Provides the series resistance of the equivalent source. |
| 4 (optional) | **Deactivate independent sources** (open current sources, short voltage sources) and compute the resistance seen into the terminals directly. | This yields the same \(R_{\text{TH}}\) without having to calculate a short‑

**Diagrams/board content from this segment:**

![Rn R OV, R (captured at 1175.0s)](D:/Documents/classroom-notes - Copy/scripts/pipeline_runs/abcd/extracted_images/video_test2_full/frame_1175.0s.png)
*This image illustrates an example of Thevenin's theorem by showing the equivalence between a complex circuit and its simplified Thevenin equivalent. The original circuit on the left consists of a 9 V voltage source in series with a 6 Ω resistor (R₁), connected to a node where a 3 Ω resistor (R₂) branches to ground and a 2 Ω resistor (R₃) leads to terminal A; the load resistor R_L is connected between terminals A and B. The equivalent circuit on the right replaces this network with a single Thevenin voltage source (V_Th) in series with a Thevenin resistance (R_Th), also driving the same load R_L across terminals A and B.*

![rem: exampli so an Boy ts i R= Ovn Dy 3FR oy 8 Vn: 62 20 3A  (captured at 1225.0s)](D:/Documents/classroom-notes - Copy/scripts/pipeline_runs/abcd/extracted_images/video_test2_full/frame_1225.0s.png)
*This slide illustrates an example of Thevenin's theorem, showing a circuit with a 9V source, a 6Ω resistor (R1), a 3Ω resistor (R2), and a 2Ω resistor (R3) connected to a load resistor (RL) at terminals A and B. The bottom section demonstrates the calculation of the Thevenin voltage ($V_{Th}$) by finding the open-circuit voltage ($V_{oc}$) across terminals A and B, resulting in a value of 3V using the voltage divider formula.*

![4a. 20, on 20 20 (captured at 1290.0s)](D:/Documents/classroom-notes - Copy/scripts/pipeline_runs/abcd/extracted_images/video_test2_full/frame_1290.0s.png)
*This image shows a circuit diagram titled "Thevenin's theorem: example," featuring a network of resistors and sources connected between terminals A and B. The circuit includes a 6 A current source in parallel with a 2 Ω resistor and a 4 Ω resistor on the left side, and a 48 V voltage source in series with a 4 Ω resistor on the right side, with two 12 Ω resistors bridging the middle sections. The diagram is set up to demonstrate finding the Thevenin equivalent circuit as seen from terminals A and B.*

![Thev rem: a0 AB 40 20, ro 30 on Rov a2 AB 40 201 ne gre AB 4 (captured at 1335.0s)](D:/Documents/classroom-notes - Copy/scripts/pipeline_runs/abcd/extracted_images/video_test2_full/frame_1335.0s.png)
*This image displays a slide titled "Thevenin's theorem: example" containing three circuit diagrams used to demonstrate the calculation of Thevenin resistance ($R_{Th}$). The top diagram shows a complex circuit with a 6 A current source, a 48 V voltage source, and resistors of 2 $\Omega$, 4 $\Omega$, and 12 $\Omega$ connected between terminals A and B. The middle diagram illustrates the circuit with independent sources turned off (current source open, voltage source shorted) to find the equivalent resistance. The bottom diagram shows the final simplified Thevenin equivalent circuit, consisting of a 4 $\Omega$ resistor in series with a 3 $\Omega$ resistor connected to terminals A and B.*


---

## Graphical Determination of Thevenin Equivalent Parameters  

In the previous analysis we found the open‑circuit voltage between terminals **A** and **B** to be  

\[
V_{AB}=V_{AC}+V_{CB}=24\ \text{V}+36\ \text{V}=60\ \text{V},
\]

and the Thevenin resistance to be  

\[
R_{TH}=7\ \Omega .
\]

Thus the Thevenin equivalent of the original network is a 60 V ideal voltage source in series with a 7 Ω resistor.  
The graphical method offers a visual way to obtain the same two quantities, \(V_{TH}\) and \(R_{TH}\), from a single plot of current versus voltage.

### 1. Constructing the I‑V Plot  

1. **Attach a variable voltage source** across the two terminals whose Thevenin model is desired.  
2. **Measure the current** that flows through the source for several values of the applied voltage.  
3. **Plot the measured current \(I\) (vertical axis) against the applied voltage \(V\) (horizontal axis).**  

Because the external source forces a voltage \(V\) across the series combination of the unknown Thevenin voltage source \(V_{TH}\) and resistance \(R_{TH}\), the circuit obeys

\[
I = \frac{V_{TH}-V}{R_{TH}}.
\]

Re‑arranging gives the straight‑line equation

\[
V = V_{TH} - I R_{TH},
\]

which is a line with **negative slope** \(-1/R_{TH}\).

### 2. Interpreting the Plot  

| Feature of the line | Physical meaning |
|---------------------|------------------|
| **X‑intercept** (where \(I=0\)) | \(V = V_{TH}\). This point is the **open‑circuit voltage** \(V_{OC}\). |
| **Y‑intercept** (where \(V=0\)) | \(I = V_{TH}/R_{TH}\). This is the **short‑circuit current** \(I_{SC}\). |
| **Slope** \(= -1/R_{TH}\) | Its magnitude yields the **Thevenin resistance** \(R_{TH}= -1/(\text{slope})\). |

Thus, from a single straight line we can read off both \(V_{TH}\) (from the voltage axis) and \(I_{SC}\) (from the current axis); dividing the former by the latter gives the resistance.

### 3. Alternative Load‑Resistor Method  

Instead of a voltage source, one may connect a **variable load resistor \(R_L\)** across the terminals and record the resulting \((V, I)\) pairs. Varying \(R_L\) traces the same line on the I‑V graph, because the relationship between terminal voltage and load current is identical:

\[
I = \frac{V_{TH}-V}{R_{TH}}.
\]

Consequently the same intercepts and slope are obtained, confirming the method’s robustness.

### 4. Applying the Method to the Example Circuit  

A simulation (SQL file `ee101.thevenin_1.sqpr`) was run with a voltage source placed between nodes **A** and **B**. The resulting I‑V curve exhibited:

- **X‑intercept:** \(V_{OC}=60\ \text{V}\) → \(V_{TH}=60\ \text{V}\).  
- **Y‑intercept:** \(I_{SC}=8.57\ \text{A}\).

From these numbers the Thevenin resistance follows immediately:

\[
R_{TH}= \frac{V_{TH}}{I_{SC}} = \frac{60\ \text{V}}{8.57\ \text{A}} \approx 7\ \Omega .
\]

These values match the analytical result obtained earlier (60 V and 7 Ω), confirming the correctness of both the algebraic and graphical approaches.

### 5. Summary of the Graphical Procedure  

- Connect a controllable source (voltage or variable resistor) across the terminals of interest.  
- Record the terminal voltage and corresponding current for several source settings.  
- Plot \(I\) versus \(V\); the data should lie on a straight line with negative slope.  
- Read the **x‑intercept** as \(V_{TH}\) (open‑circuit voltage) and the **y‑intercept** as \(I_{SC}\) (short‑circuit current).  
- Compute \(R_{TH}=V_{TH}/I_{SC}\) or obtain it directly from the slope \(-1/R_{TH}\).  

Mastering this graphical technique equips you to extract Thevenin equivalents quickly from experimental data, a skill that proves valuable when analyzing more complex networks such as RC circuits, amplifiers, and power‑distribution systems.

**Diagrams/board content from this segment:**

![for finding Bo Vn, vn Ov ‘ Vn = v 1= ~T— (Note: negative slo (captured at 1505.0s)](D:/Documents/classroom-notes - Copy/scripts/pipeline_runs/abcd/extracted_images/video_test2_full/frame_1505.0s.png)
*This slide illustrates the graphical method for determining the Thevenin equivalent voltage ($V_{Th}$) and resistance ($R_{Th}$) of a circuit. It displays a circuit diagram of a Thevenin source ($V_{Th}$ in series with $R_{Th}$) connected to a load, alongside an I-V characteristic graph where the vertical axis is Current ($I$) and the horizontal axis is Voltage ($V$). The graph shows a linear line with a negative slope, intersecting the vertical axis at $V_{Th}/R_{Th}$ and the horizontal axis at $V_{Th}$. The slide also presents the governing equation $I = \frac{V_{Th} - V}{R_{Th}}$ to mathematically describe the relationship shown in the plot.*

![49 40 20 4 120 20 © 8 (captured at 1660.0s)](D:/Documents/classroom-notes - Copy/scripts/pipeline_runs/abcd/extracted_images/video_test2_full/frame_1660.0s.png)
*This image displays an electrical circuit diagram used to demonstrate the graphical method for finding the Thevenin equivalent voltage ($V_{Th}$) and resistance ($R_{Th}$) across terminals A and B. The circuit consists of a left section with a 6 A current source in parallel with a 12 $\Omega$ resistor and a branch containing a 4 $\Omega$ resistor in series with a 2 $\Omega$ resistor. The right section features a 48 V voltage source in series with a 4 $\Omega$ resistor, connected to a parallel 12 $\Omega$ resistor. The two sections are separated by the open terminals A and B.*
