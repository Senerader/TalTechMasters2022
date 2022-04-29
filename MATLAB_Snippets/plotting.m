%% Construct plots
i = 1;
subplot(6, 1, 1);
plot(StatesPhysical.time(2:5001), StatesPhysical.signals(1).values(2:5001))
hold on;
plot(StatesVirtual.time, StatesVirtual.signals(1).values)
hold off;
legend("Action Physical","Action Virtual")
subplot(6, 1, 2);
plot(StatesPhysical.time(2:5001), StatesPhysical.signals(2).values(2:5001))
hold on;
plot(StatesVirtual.time, StatesVirtual.signals(2).values)
hold off;
legend("PendPos Physical","PendPos Virtual")
subplot(6, 1, 3);
plot(StatesPhysical.time(2:5001), StatesPhysical.signals(3).values(2:5001))
hold on;
plot(StatesVirtual.time, StatesVirtual.signals(3).values)
hold off;
legend("PendVel Physical","PendVel Virtual")
subplot(6, 1, 4);
plot(StatesPhysical.time(2:5001), StatesPhysical.signals(4).values(2:5001))
hold on;
plot(StatesVirtual.time, StatesVirtual.signals(4).values)
hold off;
legend("CartPos Physical","CartPos Virtual")
subplot(6, 1, 5);
plot(StatesPhysical.time(2:5001), StatesPhysical.signals(5).values(2:5001))
hold on;
plot(StatesVirtual.time, StatesVirtual.signals(5).values)
hold off;
legend("CartVel Physical","CartVel Virtual")
subplot(6, 1, 6);
plot(StatesPhysical.time(2:5001), StatesPhysical.signals(6).values(2:5001))
hold on;
plot(StatesVirtual.time, StatesVirtual.signals(6).values)
hold off;
legend("CtrlMode Physical","CtrlMode Virtual")