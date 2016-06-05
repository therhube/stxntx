<?php
function theme_enqueue_styles() {

    $parent_style = 'parent-style';

    wp_enqueue_style( $parent_style, get_template_directory_uri() . '/style.css' );
    wp_enqueue_style( 'child-style',
        get_stylesheet_directory_uri() . '/style.css',
        array( $parent_style )
    );
}
add_action( 'wp_enqueue_scripts', 'theme_enqueue_styles' );


function baskerville_child_meta() { ?>
<!-- AR: added this function simply to comment out the comment count link; don't need a bunch of zeroes everywhere -->

	<div class="post-meta">
	
		<a class="post-date" href="<?php the_permalink(); ?>" title="<?php the_title_attribute(); ?>"><?php the_time( 'Y m d' ); ?></a>
		
		<?php
		
			if( function_exists('zilla_likes') ) zilla_likes(); 
		
			/*if ( comments_open() ) {
				comments_popup_link( '0', '1', '%', 'post-comments' );
			}
			*/
			edit_post_link(); 
		
		?>
		
		<div class="clear"></div>
	
	</div> <!-- /post-meta -->
	
<?php
}

?>