
window.onload = () => {
    var projectDiv = document.querySelector('.form-row.field-project');

    var newDiv1 = document.createElement('div');
    projectDiv.parentNode.insertBefore(newDiv1, projectDiv.nextSibling);
    var feedbackResponsivenessDiv = document.querySelector('.form-row.field-feedback_responsiveness');
    var continuousLearningDiv = document.querySelector('.form-row.field-continuous_learning');
    newDiv1.appendChild(feedbackResponsivenessDiv);
    newDiv1.appendChild(continuousLearningDiv);


    var newDiv2 = document.createElement('div');
    projectDiv.parentNode.insertBefore(newDiv2, projectDiv.nextSibling.nextSibling);
    var collaborationDiv = document.querySelector('.form-row.field-collaboration');
    var communicationEffectivenessDiv = document.querySelector('.form-row.field-communication_effectiveness');
    newDiv2.appendChild(collaborationDiv);
    newDiv2.appendChild(communicationEffectivenessDiv);


    var newDiv3 = document.createElement('div');
    projectDiv.parentNode.insertBefore(newDiv3, projectDiv.nextSibling.nextSibling.nextSibling);
    var leadershipPotentialDiv = document.querySelector('.form-row.field-leadership_potential');
    var problemSolvingAbilityDiv = document.querySelector('.form-row.field-problem_solving_ability');
    newDiv3.appendChild(leadershipPotentialDiv);
    newDiv3.appendChild(problemSolvingAbilityDiv);


    var newDiv4 = document.createElement('div');
    projectDiv.parentNode.insertBefore(newDiv4, projectDiv.nextSibling.nextSibling.nextSibling.nextSibling);
    var innovationAndCreativityDiv = document.querySelector('.form-row.field-innovation_and_creativity');
    var adaptabilityAndFlexibilityDiv = document.querySelector('.form-row.field-adaptability_and_flexibility');
    newDiv4.appendChild(innovationAndCreativityDiv);
    newDiv4.appendChild(adaptabilityAndFlexibilityDiv);


    var newDiv5 = document.createElement('div');
    projectDiv.parentNode.insertBefore(newDiv5, projectDiv.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling);
    var professionalGrowthAndDevelopmentDiv = document.querySelector('.form-row.field-professional_growth_and_development');
    var overallContributionToTeamSuccessDiv = document.querySelector('.form-row.field-overall_contribution_to_team_success');
    newDiv5.appendChild(professionalGrowthAndDevelopmentDiv);
    newDiv5.appendChild(overallContributionToTeamSuccessDiv);


    function handleLayoutChange() {
        if (window.innerWidth >= 752) {
            newDiv1.className = 'form-row rating-fields'
            newDiv1.style.display = 'grid'; 
            newDiv1.style.gridTemplateColumns = '1fr 1fr'; 
            newDiv1.style.alignItems = 'center';
            feedbackResponsivenessDiv.classList.remove('form-row');
            continuousLearningDiv.classList.remove('form-row');
    
        
            newDiv2.className = 'form-row rating-fields'
            newDiv2.style.display = 'grid'; 
            newDiv2.style.gridTemplateColumns = '1fr 1fr'; 
            newDiv2.style.alignItems = 'center';
            collaborationDiv.classList.remove('form-row');
            communicationEffectivenessDiv.classList.remove('form-row');
        

            newDiv3.className = 'form-row rating-fields'
            newDiv3.style.display = 'grid'; 
            newDiv3.style.gridTemplateColumns = '1fr 1fr'; 
            newDiv3.style.alignItems = 'center';
            leadershipPotentialDiv.classList.remove('form-row');
            problemSolvingAbilityDiv.classList.remove('form-row');
        

            newDiv4.className = 'form-row rating-fields'
            newDiv4.style.display = 'grid'; 
            newDiv4.style.gridTemplateColumns = '1fr 1fr';
            newDiv4.style.alignItems = 'center';
            innovationAndCreativityDiv.classList.remove('form-row');
            adaptabilityAndFlexibilityDiv.classList.remove('form-row');
        
            
            newDiv5.className = 'form-row rating-fields'
            newDiv5.style.display = 'grid'; 
            newDiv5.style.gridTemplateColumns = '1fr 1fr';
            newDiv5.style.alignItems = 'center';
            professionalGrowthAndDevelopmentDiv.classList.remove('form-row');
            overallContributionToTeamSuccessDiv.classList.remove('form-row');
        
            
        }

        else{
            newDiv1.classList.remove('form-row');
            newDiv1.style.display = ''; 
            newDiv1.style.gridTemplateColumns = ''; 
            newDiv1.style.alignItems = '';
            feedbackResponsivenessDiv.classList.add('form-row');
            continuousLearningDiv.classList.add('form-row');

            newDiv2.classList.remove('form-row');
            newDiv2.style.display = ''; 
            newDiv2.style.gridTemplateColumns = ''; 
            newDiv2.style.alignItems = '';
            collaborationDiv.classList.add('form-row');
            communicationEffectivenessDiv.classList.add('form-row')

            newDiv3.classList.remove('form-row');
            newDiv3.style.display = ''; 
            newDiv3.style.gridTemplateColumns = ''; 
            newDiv3.style.alignItems = '';
            leadershipPotentialDiv.classList.add('form-row');
            problemSolvingAbilityDiv.classList.add('form-row')


            newDiv4.classList.remove('form-row');
            newDiv4.style.display = ''; 
            newDiv4.style.gridTemplateColumns = ''; 
            newDiv4.style.alignItems = '';
            innovationAndCreativityDiv.classList.add('form-row');
            adaptabilityAndFlexibilityDiv.classList.add('form-row')


            newDiv5.classList.remove('form-row');
            newDiv5.style.display = ''; 
            newDiv5.style.gridTemplateColumns = ''; 
            newDiv5.style.alignItems = '';
            professionalGrowthAndDevelopmentDiv.classList.add('form-row');
            overallContributionToTeamSuccessDiv.classList.add('form-row')

        }
    }
    handleLayoutChange();

    window.addEventListener('resize', handleLayoutChange);
}