function [sol, fval, exitflag, output] = ...
    fminvis2(funfcn, x0, lb, ub)
%VISOPT2 Uses OPTIMIZE function to solve and visualize a 2nd order problem

% Check that the problem is two dimensional
if (max(x0)>2 && min(x0)>1)
    error('The visualizer can only work for 2 dimensional problems only.');
end

% Create the figure
h = figure();
xlabel('x_1');
ylabel('x_2');

% Contours are only drawn if bounds are specified
if (nargin == 4 && ~isempty(lb) && ~isempty(ub))
    numlevels = 70;
    disp('Creating contour plot...');
    numpts = 1000;
    minp = min(lb);
    maxp = max(ub);
    xrange = linspace(minp, maxp, numpts);
    yrange = linspace(minp, maxp, numpts);
    z = zeros(numpts,numpts);
    for k=1:numpts
        for l=1:numpts
            z(l,k) = funfcn([xrange(k),yrange(l)]);
        end
    end
    
    contour(xrange,yrange,z,numlevels);
    drawnow;
    disp('Done');
end

% Default bounds: none, axes limits evolve
xb = [];
yb = [];

if nargin < 3 || isempty(lb) || isempty(ub)
    
else
    % Determine the upper and lower bounds
    xb = [lb(1) ub(1)];
    yb = [lb(2) ub(2)];
end

% Set output function
options = optimset();
options.Display = 'iter';
options.OutputFcn = @(x, optimValues, state) ...
    visopt2_outputfcn(x, optimValues, state, h, xb, yb);

[sol, fval, exitflag, output] = fminsearch1(funfcn, x0, options);

end

% This is the function that shall draw the triangles and pause simulation
function stop = visopt2_outputfcn(x, optimValues, state, h, xb, yb)
    
    % Set the correct figure
    figure(h);
    grid on;
    
    % Draw all of the parameters
    hold on;
    
    % Iteration number
    iter = optimValues.iteration;
    
    % Get the simplex out of there
    simplex = optimValues.simplex;
	
	% Function value
	fval = optimValues.fval;
    
    % Plot the triangle (but not on 0 iteration)
    if iter>0
        tri(simplex);
        title(['Current values: x_1 = '  num2str(x(1)) ...
                ', x_2 = ' num2str(x(2)) ', f = ' num2str(fval)]);
    end
    
    drawnow;
    
    pause(0.5);
    
    % Set bounds (only on 0 iteration)
    if (~isempty(xb) && ~isempty(yb))
        xlim(xb); ylim(yb);
    end
    
    stop = 0;
end