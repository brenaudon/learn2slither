NAME			:=	learn2slither

SRC				:=	src/cpp/learn2slither.cpp

SRC_OBJS		:=	$(SRC:%.cpp=.build/%.o)
DEPS			:=	$(SRC_OBJS:%.o=%.d)

CXX				:=	c++
CXXFLAGS		:=	-Wall -Wextra -Werror -std=c++17 -g -O3
CPPFLAGS		:=	-MP -MMD -Isrc/cpp/include
LDFLAGS			:=

MAKEFLAGS		+= --silent --no-print-directory

all: $(NAME)

$(NAME): $(SRC_OBJS)
	$(CXX) $(CXXFLAGS) $(SRC_OBJS) $(LDFLAGS) -o $(NAME)
	@printf "%b" "$(BLUE)CREATED $(CYAN)$(NAME)\n"

.build/%.o: %.cpp
	mkdir -p $(@D)
	$(CXX) $(CXXFLAGS) -c $(CPPFLAGS) $< -o $@
	@printf "%b" "$(BLUE)CREATED $(CYAN)$@\n"

-include $(DEPS)

clean:
	rm -rf .build

fclean: clean
	rm -rf $(NAME)

re:
	$(MAKE) fclean
	$(MAKE) all

.PHONY: all clean fclean re