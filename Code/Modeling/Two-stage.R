# two stage model based on Hu et al 2014

#Step one: mixed effects model. 

library(lme4)
# example: gpa_mixed = lmer(gpa ~ occasion + (1|student), data = **)