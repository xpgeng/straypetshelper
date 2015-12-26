$(window).load(function () {


var button = 1;
var button_class = "gallery-header-center-right-links-current";
var $containerTest = $('.photowall');
    
$containerTest.isotope({
	itemSelector : '.pet',	
	masonry:{
		isFitWidth: true
	}
 });


function check_button(){
	$('.gallery-header-center-right-links').removeClass(button_class);
	if(button==1){
		$("#filter-all").addClass(button_class);
		}
	if(button==2){
		$("#filter-cat").addClass(button_class);
		}
	if(button==3){
		$("#filter-dog").addClass(button_class);
		}	
}
	
	
$("#filter-all").click(function() { $containerTest.isotope({ filter: '.pet' }); button = 1; check_button(); });
$("#filter-cat").click(function() {  $containerTest.isotope({ filter: '.Spe-c' }); button = 2; check_button();  });
$("#filter-dog").click(function() {  $containerTest.isotope({ filter: '.Spe-d' }); button = 3; check_button();  });


check_button();
});