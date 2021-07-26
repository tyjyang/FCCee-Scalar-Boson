text2workspace.py datacard_combined_0p5_auto.txt -m 0.5 -o workspace_0p5.root
combine -M AsymptoticLimits workspace_0p5.root -t -1 --expectSignal 0 -m 0.5 --X-rtd MINIMIZER_analytic

text2workspace.py datacard_combined_2_auto.txt -m 2 -o workspace_2.root
combine -M AsymptoticLimits workspace_2.root -t -1 --expectSignal 0 -m 2 --X-rtd MINIMIZER_analytic

text2workspace.py datacard_combined_5_auto.txt -m 5 -o workspace_5.root
combine -M AsymptoticLimits workspace_5.root -t -1 --expectSignal 0 -m 5 --X-rtd MINIMIZER_analytic

text2workspace.py datacard_combined_10_auto.txt -m 10 -o workspace_10.root
combine -M AsymptoticLimits workspace_10.root -t -1 --expectSignal 0 -m 10 --X-rtd MINIMIZER_analytic 

text2workspace.py datacard_combined_15_auto.txt -m 15 -o workspace_15.root
combine -M AsymptoticLimits workspace_15.root -t -1 --expectSignal 0 -m 15 --X-rtd MINIMIZER_analytic

text2workspace.py datacard_combined_25_auto.txt -m 25 -o workspace_25.root
combine -M AsymptoticLimits workspace_25.root -t -1 --expectSignal 0 -m 25 --X-rtd MINIMIZER_analytic

python make_limit_plot.py
