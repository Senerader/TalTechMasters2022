function [sol, fval, exitflag, output] = ...
    fminvis3(funfcn, x0, lb, ub)
%VISOPT3 Solves and visualize a 2nd order problem with NM in a 3D space

% Check that the problem is two dimensional
if (max(x0)>2 && min(x0)>1)
    error('The visualizer can only work for 2 dimensional problems only.');
end

% Create the figure
numpts = 100;
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

h = figure();
surf(xrange,yrange,z);
ax = gca;
ax.Clipping = 'off';
colorbar;
xlabel('x_1');
ylabel('x_2');
zlabel('y');


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
    visopt2_outputfcn(x, optimValues, state, h, xb, yb, funfcn);

[sol, fval, exitflag, output] = fminsearch1(funfcn, x0, options);

end

% This is the function that shall draw the triangles and pause simulation
function stop = visopt2_outputfcn(x, optimValues, state, h, xb, yb, funfcn)

	% Get iteration number
	iter = optimValues.iteration;
    
    % Set the correct figure
    figure(h);
    grid on;
    
    % Draw all of the parameters
    hold on;
    
    % Get the simplex out of there
    simplex = optimValues.simplex;
	
	% Function value
	fval = optimValues.fval;
    
    % Plot the triangle (not on first iteration)
	if (iter>0)
		trid(simplex, funfcn);
		title(['Current values: x_1 = '  num2str(x(1)) ...
				', x_2 = ' num2str(x(2)) ', f = ' num2str(fval)]);
	end
    
    drawnow;
    
    pause(0.5);
    
    % Set bounds (only on first iteration)
	if iter == 0
		if (~isempty(xb) && ~isempty(yb))
			xlim(xb); ylim(yb);
		end	
	end
    
    stop = 0;
end