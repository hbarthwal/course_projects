%program for Genetic algorithm to maximize the function f(x) =sin(x)
clear all;
clc;
%x ranges from 0 to 3.14
%five bits are enough to represent x in binary representation
n=input('Enter no. of population in each iteration');
nit=input('Enter no. of iterations');
%Generate the initial population
[oldchrom]=initbp(n,5);
%The population in binary is converted to integer
FieldD=[5;0;3.14;0;0;1;1]
for i=1:nit
phen=bindecod(oldchrom,FieldD,3);% phen gives the integer value of the
%binary population
%obtain fitness value
FitnV=sin(phen);
%apply roulette wheel selection
Nsel=4;
newchrix=selrws(FitnV, Nsel);
newchrom=oldchrom(newchrix,:);
%Perform Crossover
crossoverrate=1;
newchromc=recsp(newchrom,crossoverrate);%new population after crossover
%Perform mutation
vlub=0:31;
mutationrate=0.001;
newchromm=mutrandbin(newchromc,vlub,mutationrate);%new population
%after mutation
disp('For iteration');
i
disp('Population');
oldchrom
disp('X');
phen
disp('f(X)');
FitnV
oldchrom=newchromm;
end