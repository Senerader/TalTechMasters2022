% Anonymous function handler
optimizer_pend=@(x) function_optimizer_pendulum_all(x(1));

% Option to optimize
options = optimset('PlotFcns',@optimplotfval);
% mc, mp, fp, FS, FC, I, J, g, M, DZu, DZcv, DZcp
x0 = [
    0.5723 
    0.12 
    0.00027344 
    1.1975875 
    0.5 
    0.019557 
    0.003858 
    9.81 
    6.3
    0.093125 
    0.1 
    1.5]; % Initial solution
% mc, mp, fp, FS, FC, I, J, g, M, DZu, DZcv, DZcp
lb = [
    0 
    0 
    0 
    0 
    0 
    0 
    0 
    0  
    0 
    0 
    0 
    0];
% mc, mp, fp, FS, FC, I, J, g, M, DZu, DZcv, DZcp
ub = [
    1 
    1 
    0.01 
    2 
    1.5 
    0.1 
    0.01 
    15
    13
    2 
    1 
    3];
options = optimset('Display','iter', 'TolX',1e-7);
x = fminsearchbnd(@function_optimizer_pendulum_all, x0, lb, ub, options)