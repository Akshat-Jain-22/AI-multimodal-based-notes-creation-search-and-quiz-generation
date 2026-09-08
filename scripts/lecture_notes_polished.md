# Basic Electronics - Thevenin's Theorem

This lecture covers Thevenin's theorem, a fundamental concept in electronics that allows us to represent a complex circuit with a simpler equivalent form. The theorem is crucial for simplifying circuit analysis and understanding circuit behavior under various conditions. By applying Thevenin's theorem, we can replace a complex circuit with a single voltage source in series with a resistance, facilitating easier analysis and calculation of circuit behaviors.

## Introduction to Thevenin's Theorem and Its Application

Thevenin's theorem is based on the idea of representing a complex circuit with a simpler equivalent form, consisting of a single voltage source in series with a resistance. To understand this concept, let's consider a circuit with a load resistor $R_L$, where we're interested in finding the voltage across $R_L$. We assign node voltages to various points in the circuit with respect to a reference node. By applying Kirchhoff's Current Law (KCL) at each node, we can write equations in terms of these node voltages. For instance, at node A, we have three currents: one leaving the node through $R_1$, one through $R_2$, and an external current $I_0$ entering the node. We define conductances $G_1$, $G_2$, etc., as the reciprocals of the corresponding resistances, i.e., $G_1 = \frac{1}{R_1}$, $G_2 = \frac{1}{R_2}$, and so on.

Using these definitions, we can express the KCL equation at node A as $G_1(V_1 - V_3) + G_2(V_1 - V_2) - I_0 = 0$. Similarly, we can write KCL equations for nodes B and C, resulting in a system of linear equations. By arranging these equations in a matrix form, we obtain a $3 \times 3$ matrix equation, where the matrix $G$ represents the conductances between nodes, $V$ is the column vector of node voltages, and $I_s$ is the source current vector.

Our objective is to find a relationship between $V$ and the rest of the circuit. To do this, we need to solve the matrix equation $G \cdot V = I_s$ for the node voltage $V_2$, which is equivalent to the voltage $V$ across the load resistor $R_L$. One way to achieve this is by using Kramer's rule, which states that $V_2$ can be found by taking the ratio of two determinants: $D_1$, the determinant of the matrix $G$ with the second column replaced by the RHS vector, and $D_2$, the determinant of the original matrix $G$.

![~ NPTEL (captured at 5.0s)](extracted_images/test2_full/frame_5.0s.png)
*~ NPTEL (captured at 5.0s)*

![BASIC ELECTRONICS mst - (captured at 10.0s)](extracted_images/test2_full/frame_10.0s.png)
*BASIC ELECTRONICS mst - (captured at 10.0s)*

![The, Re Oe R ‘ oN How is V related tothe circuit parameters? (captured at 60.0s)](extracted_images/test2_full/frame_60.0s.png)
*The, Re Oe R ‘ oN How is V related tothe circuit parameters? (captured at 60.0s)*

By simplifying the expression obtained from Kramer's rule, we can establish a relationship between $V$ and the circuit parameters. This relationship will allow us to represent the complex circuit with a simpler Thevenin equivalent form.

## Deriving the Thevenin Equivalent Circuit

To find the voltage $V_2$, we apply Cramer's rule, which states that $V_2$ is given by the ratio of two determinants: the determinant of the original $G$ matrix with the second column replaced with the RHS vector, and the determinant of the $G$ matrix itself. Let's denote the first determinant as $\delta_1$ and the second as $\delta$. Notice that $\delta_1$ does not depend on the load resistance $R_L$ or $G_L$, making its value independent of the load resistance.

The determinant of the $G$ matrix, $\delta$, does depend on $G_L$. To simplify this, we can express one of the columns in the $G$ matrix as the sum of two columns, allowing us to write the determinant $\delta$ as the sum of two determinants. One of these determinants, denoted as $\delta$, has no $G_L$ term, while the other, $G_L$ times $\delta_2$, does contain $G_L$. By making this substitution, we can express $V_2$ as $\frac{\delta_1}{\delta + G_L\delta_2}$. The key point here is that $\delta_1$, $\delta$, and $\delta_2$ are all independent of $G_L$.

The only dependence of $V_2$ on $G_L$ is through the term $G_L\delta_2$ in the denominator. To further simplify the expression for $V_2$, we notice that $\frac{\delta_2}{\delta}$ has units of resistance. Therefore, we define the Thevenin resistance $R_{Thevenin}$ as $\frac{\delta_2}{\delta}$. With this definition, the expression for $V_2$ simplifies to $V_2 = \frac{R_L}{R_L + R_{Thevenin}} \cdot V_{2_{OC}}$, where $V_{2_{OC}}$ is the open-circuit value of $V_2$, obtained by letting $R_L$ approach infinity (or equivalently, $G_L$ approach 0).

This expression for $V_2$ closely resembles the voltage division formula. In fact, it corresponds to a circuit where $V_{2_{OC}}$ is the voltage source, $R_{Thevenin}$ and $R_L$ are in series, and $V_2$ is the voltage across $R_L$. This realization allows us to replace the original circuit with a simpler, equivalent circuit known as the Thevenin equivalent circuit. The Thevenin equivalent circuit consists of a voltage source $V_{Thevenin} = V_{2_{OC}}$ in series with the Thevenin resistance $R_{Thevenin}$.

$$V_{TH} = \frac{R_L}{R_L + R_{TH}} V_{OC}$$

![Thevenin Ri 5 Rev Ve can be found using Cramer's rule: Ve = (captured at 370.0s)](extracted_images/test2_full/frame_370.0s.png)
*Thevenin Ri 5 Rev Ve can be found using Cramer's rule: Ve = (captured at 370.0s)*

![az Ov nev Va can be found using Cramer's rule: Ve = Gs dex(6 (captured at 445.0s)](extracted_images/test2_full/frame_445.0s.png)
*az Ov nev Va can be found using Cramer's rule: Ve = Gs dex(6 (captured at 445.0s)*

## Determining Thevenin Equivalent Circuits

To find the Thevenin equivalent of a circuit, we need to determine two key components: the Thevenin voltage ($V_{TH}$) and the Thevenin resistance ($R_{TH}$). The Thevenin voltage is equivalent to the open-circuit voltage ($V_{OC}$) between the two points of interest. When the circuit is open-circuited, the voltage measured between these points is the Thevenin voltage.

The short-circuit current ($I_{SC}$) is another crucial component in finding $R_{TH}$. $I_{SC}$ is the current that flows between points A and B when they are directly connected, or short-circuited. Since there's no other resistance in the circuit when A and B are short-circuited, $I_{SC}$ is simply $V_{TH}$ divided by $R_{TH}$. Knowing that $V_{TH}$ equals $V_{OC}$, we can say that $I_{SC}$ equals $V_{OC}$ divided by $R_{TH}$. This relationship gives us a formula to calculate $R_{TH}$: $R_{TH}$ equals $V_{OC}$ divided by $I_{SC}$.

![Rr Circuit A A (resistors, ‘ sources, Vm Cevs, Coes, vevs, v (captured at 765.0s)](extracted_images/test2_full/frame_765.0s.png)
*Rr Circuit A A (resistors, ‘ sources, Vm Cevs, Coes, vevs, v (captured at 765.0s)*

To find $V_{TH}$, we can use the fact that the open-circuit voltage between A and B in both the original circuit and its Thevenin equivalent must be the same. By measuring the open-circuit voltage, $V_{OC}$, between A and B in the original circuit, we can determine $V_{TH}$, as it is equal to $V_{OC}$. On the other hand, finding $R_{TH}$ can be done through several methods. One approach is to deactivate all independent sources in the original circuit and then find the resistance between A and B. This resistance will be equal to $R_{TH}$.

Let's consider an example to illustrate this concept. Suppose we have a circuit with a voltage source and resistors, and we want to find its Thevenin equivalent as seen from points A and B. To find $V_{TH}$, we remove the load (in this case, $R_L$) and calculate the open-circuit voltage between A and B. This can often be done using voltage division.

![Rn R OV, R (captured at 1175.0s)](extracted_images/test2_full/frame_1175.0s.png)
*Rn R OV, R (captured at 1175.0s)*

![rem: exampli so an Boy ts i R= Ovn Dy 3FR oy 8 Vn: 62 20 3A  (captured at 1225.0s)](extracted_images/test2_full/frame_1225.0s.png)
*rem: exampli so an Boy ts i R= Ovn Dy 3FR oy 8 Vn: 62 20 3A  (captured at 1225.0s)*

![4a. 20, on 20 20 (captured at 1290.0s)](extracted_images/test2_full/frame_1290.0s.png)
*4a. 20, on 20 20 (captured at 1290.0s)*

## Finding Thevenin's Voltage and Resistance Using Graphical Methods

To determine Thevenin's voltage ($V_{TH}$) and resistance ($R_{TH}$) graphically, we can utilize a method involving voltage division and a plot of current versus voltage. Let's begin with the given circuit, where $V_{CB}$ is determined by voltage division of 48 volts between 12 ohms and 4 ohms, resulting in 36 volts. Consequently, the total voltage between points A and B is the sum of $V_{AC}$ (24 volts) and $V_{CB}$ (36 volts), which equals 60 volts. This total voltage is equivalent to $V_{TH}$.

![for finding Bo Vn, vn Ov ‘ Vn = v 1= ~T— (Note: negative slo (captured at 1505.0s)](extracted_images/test2_full/frame_1505.0s.png)
*for finding Bo Vn, vn Ov ‘ Vn = v 1= ~T— (Note: negative slo (captured at 1505.0s)*

The graphical approach for finding $V_{TH}$ and $R_{TH}$ involves connecting a voltage source between points A and B in the circuit and then plotting the current as a function of the voltage. The plot obtained has a negative slope, given by the equation $I = \frac{V_{TH} - V}{R_{TH}}$, where the slope of the line is $-\frac{1}{R_{TH}}$. The x-intercept of this line corresponds to $V_{TH}$ (or $V_{OC}$, the open-circuit voltage), while the y-intercept represents the short-circuit current ($I_{SC}$), which is $\frac{V_{TH}}{R_{TH}}$.

By analyzing this plot, we can directly determine $V_{TH}$ and $R_{TH}$. Applying this graphical method to a circuit involves connecting a voltage source between the points of interest (A and B) and measuring the current for various voltages. The resulting plot of current versus voltage allows us to find $V_{TH}$ as the intercept on the voltage axis and $I_{SC}$ (which equals $\frac{V_{TH}}{R_{TH}}$) as the intercept on the current axis.

## Key Takeaways

* Thevenin's theorem allows us to represent a complex circuit with a simpler equivalent form, consisting of a single voltage source in series with a resistance.
* The Thevenin voltage ($V_{TH}$) is equivalent to the open-circuit voltage ($V_{OC}$) between the two points of interest.
* The Thevenin resistance ($R_{TH}$) can be found by deactivating all independent sources in the original circuit and then finding the resistance between the points of interest.
* The graphical method involves plotting current versus voltage and using the slope and intercepts to find $V_{TH}$ and $R_{TH}$.
* Thevenin's theorem is a powerful tool for simplifying complex circuits and facilitating easier analysis and calculation of circuit behaviors.