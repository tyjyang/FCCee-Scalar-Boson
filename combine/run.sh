text2workspace.py datacard_0p5.txt -m 0.5 -o workspace_0p5.root
combine -M AsymptoticLimits workspace_0p5.root -t -1 --expectSignal 0 -m 0.5
text2workspace.py datacard_2.txt -m 2 -o workspace_2.root
combine -M AsymptoticLimits workspace_2.root -t -1 --expectSignal 0 -m 2 
text2workspace.py datacard_5.txt -m 5 -o workspace_5.root
combine -M AsymptoticLimits workspace_5.root -t -1 --expectSignal 0 -m 5
text2workspace.py datacard_10.txt -m 10 -o workspace_10.root
combine -M AsymptoticLimits workspace_10.root -t -1 --expectSignal 0 -m 10 
text2workspace.py datacard_15.txt -m 15 -o workspace_15.root
combine -M AsymptoticLimits workspace_15.root -t -1 --expectSignal 0 -m 15
text2workspace.py datacard_25.txt -m 25 -o workspace_25.root
combine -M AsymptoticLimits workspace_25.root -t -1 --expectSignal 0 -m 25
python make_limit_plot.py
