import ROOT
import sys,os
from array import array


ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)


def makePlotUpperLimit():


    ##########################
    # retrieve results from combine
    ##########################

    output_txt = "RESULTS COMBINE (text)\n"
    output_txt += "----------------------\n\n"
    output_txt += "mass\t-2s\t-1s\texp\t+1s\t+2s\n"
    
    
    # create some arrays to hold the results values
    mass = array('d',[])
    zeros = array('d',[])
    exp_p2 = array('d',[])
    exp_p1 = array('d',[])
    exp = array('d',[])
    exp_m1 = array('d',[])
    exp_m2 = array('d',[])
    obs = array('d',[])


    # loop over the mass values and fill the arrays
    for i,m in enumerate(masses):
        
        fIn = combine_files[i]
        if not os.path.isfile(fIn): continue
        
        f = ROOT.TFile(fIn, "READ")
        t = f.Get("limit")
        if not t: continue
        
        output_txt += str(int(m)) + "\t"
        
        
        mass.append(m)

        
        # expected limit
        t.GetEntry(2)
        thisexp = t.limit
        #print t.limit, thisexp, m
        exp.append(thisexp)
        
        #-2 sigma
        t.GetEntry(0)
        m2s = t.limit
        exp_m2.append(thisexp-m2s)
        output_txt += "%.4f\t" % (m2s)

        
        #-1 sigma
        t.GetEntry(1)
        m1s = t.limit
        exp_m1.append(thisexp-m1s)
        output_txt += "%.4f\t" % (m1s)
        
        # expected limit
        output_txt += "%.4f\t" % thisexp
        
        #+1 sigma 
        t.GetEntry(3)
        p1s = t.limit
        exp_p1.append(p1s-thisexp)
        output_txt += "%.4f\t" % (p1s)
        
        #+2 sigma
        t.GetEntry(4)
        p2s = t.limit
        exp_p2.append(p2s-thisexp)
        output_txt += "%.4f\n" % (p2s)
       
        
        
        # dummy array with 0.0 (for mass-uncertainty)
        zeros.append(0.0)
        
        

    # convert arrays to TVectorD (needed for TGraphs)
    v_mass = ROOT.TVectorD(len(mass),mass)
    v_zeros = ROOT.TVectorD(len(zeros),zeros)
    v_exp_p2 = ROOT.TVectorD(len(exp_p2),exp_p2)
    v_exp_p1 = ROOT.TVectorD(len(exp_p1),exp_p1)
    v_exp = ROOT.TVectorD(len(exp),exp)
    v_exp_m1 = ROOT.TVectorD(len(exp_m1),exp_m1)
    v_exp_m2 = ROOT.TVectorD(len(exp_m2),exp_m2)




    ##########################
    # start plotting
    ##########################
    gr_exp2 =  ROOT.TGraphAsymmErrors(v_mass,v_exp,v_zeros,v_zeros,v_exp_m2,v_exp_p2)
    gr_exp1 =  ROOT.TGraphAsymmErrors(v_mass,v_exp,v_zeros,v_zeros,v_exp_m1,v_exp_p1)
    gr_exp =  ROOT.TGraphAsymmErrors(v_mass,v_exp,v_zeros,v_zeros,v_zeros,v_zeros)

    canvas = ROOT.TCanvas("c", "c", 800, 800)
    canvas.SetTopMargin(0.055)
    canvas.SetRightMargin(0.05)
    canvas.SetLeftMargin(0.15)
    canvas.SetBottomMargin(0.11)



    # make dummy histogram to set the axis etc.
    dummy = ROOT.TH1D("h", "h", 1, min(masses), max(masses))

    dummy.GetXaxis().SetTitle(cfg_xtitle)
    dummy.GetXaxis().SetRangeUser(min(masses), max(masses))
    dummy.GetXaxis().SetTitleFont(43)
    dummy.GetXaxis().SetTitleSize(32)
    dummy.GetXaxis().SetLabelFont(43)
    dummy.GetXaxis().SetLabelSize(28)
    dummy.GetXaxis().SetTitleOffset(1.2*dummy.GetXaxis().GetTitleOffset())
    dummy.GetXaxis().SetLabelOffset(1.2*dummy.GetXaxis().GetLabelOffset())


    dummy.GetYaxis().SetTitle(cfg_ytitle)
    dummy.GetYaxis().SetRangeUser(cfg_ymin, cfg_ymax)
    dummy.SetMaximum(cfg_ymax)
    dummy.SetMinimum(cfg_ymin)
    dummy.GetYaxis().SetTitleFont(43)
    dummy.GetYaxis().SetTitleSize(32)
    dummy.GetYaxis().SetLabelFont(43)
    dummy.GetYaxis().SetLabelSize(28)
    dummy.GetYaxis().SetTitleOffset(1.7*dummy.GetYaxis().GetTitleOffset())
    dummy.GetYaxis().SetLabelOffset(1.4*dummy.GetYaxis().GetLabelOffset())
    
    dummy.Draw("HIST")
    
    gr_exp2 = ROOT.TGraphAsymmErrors(v_mass,v_exp,v_zeros,v_zeros,v_exp_m2,v_exp_p2)
    gr_exp2.SetLineColor(ROOT.kOrange)
    gr_exp2.SetFillColor(ROOT.kOrange)
    gr_exp2.Draw("E3 SAME")

    gr_exp1 = ROOT.TGraphAsymmErrors(v_mass,v_exp,v_zeros,v_zeros,v_exp_m1,v_exp_p1)
    gr_exp1.SetLineColor(ROOT.kGreen+1)
    gr_exp1.SetFillColor(ROOT.kGreen+1)
    gr_exp1.Draw("E3 SAME")

    gr_exp = ROOT.TGraphAsymmErrors(v_mass,v_exp,v_zeros,v_zeros,v_zeros,v_zeros)
    gr_exp.SetLineColor(600)
    gr_exp.SetLineWidth(3)
    gr_exp.SetLineStyle(2)
    gr_exp.Draw("L SAME")
    ROOT.gPad.SetLogy() 

    # legend
    top = 0.9
    nitems = 3
    leg = ROOT.TLegend(0.5, top-nitems*0.3/5., 0.99-(nitems-4)*0.03, top)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0) #1001
    leg.SetFillColor(0)
    leg.SetHeader("95% CL upper limits")
    leg.AddEntry(gr_exp, "Median expected", "l")
    leg.AddEntry(gr_exp1, "68% expected", "f")
    leg.AddEntry(gr_exp2, "95% expected", "f")
    leg.Draw("same")


    canvas.Modify()
    canvas.Update()

    # draw lumi 
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.045)
    latex.SetTextColor(1)
    latex.SetTextFont(42)
    latex.SetTextAlign(33)
    latex.DrawLatex(0.95, 0.995, "115.4 fb^{-1} \sqrt{s} = 91.2GeV ")

    # draw CMS preliminary
    latex.SetTextAlign(13)
    latex.SetTextFont(42)
    latex.SetTextSize(0.045)
    latex.DrawLatex(0.15, 0.985, "#bf{FCC-ee} #scale[0.7]{#it{Performance}}")
    
    
    ROOT.gPad.SetTicks()
    canvas.SetGrid()
    ROOT.gPad.RedrawAxis()
    ROOT.gPad.RedrawAxis("G")
    canvas.SaveAs(fout)        
    canvas.SaveAs(fout.replace(".png", ".pdf"))  
    

    print output_txt
   


if __name__ == "__main__":

    masses = [0.5, 2, 5, 10, 15, 25]
    combine_files = ["higgsCombineTest.AsymptoticLimits.mH0.5.root", 
                     "higgsCombineTest.AsymptoticLimits.mH2.root",
                     "higgsCombineTest.AsymptoticLimits.mH5.root",
                     "higgsCombineTest.AsymptoticLimits.mH10.root",
                     "higgsCombineTest.AsymptoticLimits.mH15.root",
                     "higgsCombineTest.AsymptoticLimits.mH25.root"]

    
    cfg_xtitle = "m_{S^{0}} (GeV)"
    cfg_ytitle = " limit on k for (#sigma_{S^{0}Z^{0}} = k * #sigma_{H^{0}Z^{0}} (m_{H^{0}_{SM}} = m_{S^{0}}))"
    
    cfg_ymin, cfg_ymax = 0.01, 3 
    
    fout = "limitPlot.png"

    makePlotUpperLimit()
