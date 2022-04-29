function tri(m)
%TRI Draw a triangle based on pairs of points

% Make sure we know what we're doing
if size(m,1) > size(m,2)
    m = m.';
end

% Get points
p1 = [m(1,1) m(2,1)];
p2 = [m(1,2) m(2,2)];
p3 = [m(1,3) m(2,3)];

% Draw lines that make up the triangle
line_2d_pts(p1,p2);
line_2d_pts(p1,p3);
line_2d_pts(p2,p3);

end

% This is a more coherent way to plot lines for a triangle
function line_2d_pts(A, B, varargin)
	line([A(1) B(1)], [A(2) B(2)], varargin{:});
end