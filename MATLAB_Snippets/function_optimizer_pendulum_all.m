function [rmse] = function_optimizer_pendulum_all(x)
    mc = x(1);
    mp = x(2);
    fp = x(3);
    FS = x(4);
    FC = x(5);
    I = x(6);
    J = x(7);
    g = x(8);
    M = x(9);
    DZu = x(10);
    DZcv = x(11);
    DZcp = x(12);
    simopt=simset('solver','ode5','SrcWorkspace','base', 'FixedStep', 0.01);
    load('OLTestData');
    set_param('pidvirtual/Dynamics', 'm', sprintf('[%f, %f]', mc, mp), ... 
                                     'fr', sprintf('[%f, %f, %f]', fp, FS, FC), ...
                                     'P4', sprintf('[%f, %f, %f]', I, J, g), ...
                                     'Up', sprintf('[%f, %f]', M, DZu), ...
                                     'DZ', sprintf('[%f, %f]', DZcv, DZcp));
    sim('IntecoVirtualOptimisation.slx',[0 120],simopt);
    StatesMatrix = new_states;
    optimized_sin = sin(StatesOptimization.Data(2:12001, 1));
    physical_sin = sin(StatesMatrix(2:12001, 2));
    optimized_cos = cos(StatesOptimization.Data(2:12001, 1));
    physical_cos = cos(StatesMatrix(2:12001, 2));
    optimized_cart = StatesOptimization.Data(2:12001, 3);
    physical_cart = StatesMatrix(2:12001, 4);
    rmse = 0.75*sqrt(sum((optimized_cart - physical_cart).^2)/ 12000) + ...
            0.25*(sqrt(sum((optimized_sin - physical_sin).^2)/ 12000) + ...
            sqrt(sum((optimized_cos - physical_cos).^2)/ 12000));
    clear StatesOptimization;
end

