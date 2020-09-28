W = 1000 * 1.602e-19
m = 1.672e-27
v = (2 * W / m) ** 0.5

r_outer = 3 / 100
r_inner = 2.4 / 100
r_mid = 2.7 / 100

Required_val = 2 * W / r_mid

q = 1.6e-19
B = 0.2


B_val = q * v * B
d = r_outer - r_inner

E1 = (B_val - Required_val) / q
E2 = (B_val + Required_val) / q

U1, U2 = E1 * d, E2 * d

print(U1, U2)
