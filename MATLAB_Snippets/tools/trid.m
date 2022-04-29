function trid(m, fun)
%TRI Draw a triangle based on pairs of points

% Make sure we know what we're doing
if size(m,1) > size(m,2)
    m = m.';
end

% Need three Z points
z1 = fun([m(1,1), m(2,1)]);
z2 = fun([m(1,2), m(2,2)]);
z3 = fun([m(1,3), m(2,3)]);

% The three points
p1 = [m(1,1), m(2,1), z1];
p2 = [m(1,2), m(2,2), z2];
p3 = [m(1,3), m(2,3), z3];

% Now just draw three lines that make a triangle
line_3d_pts(p1, p2, 'color', 'red');
line_3d_pts(p1, p3, 'color', 'red');
line_3d_pts(p1, p3, 'color', 'red');

end

% This is a more coherent way to plot lines for a triangle
function line_3d_pts(A, B, varargin)
	line([A(1) B(1)], [A(2) B(2)], [A(3) B(3)], varargin{:});
end
