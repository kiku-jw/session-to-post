We split one large publish script into a smaller content pipeline and a separate publish adapter.

The useful lesson was simple:

- the draft generator should not know too much about the final website
- publishing is where environment-specific details belong
- the editor pass removed half the filler and made the post usable
